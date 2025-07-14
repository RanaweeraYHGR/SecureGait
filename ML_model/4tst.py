import cv2
import mediapipe as mp
import numpy as np
import joblib
import pandas as pd
from datetime import datetime
import RPi.GPIO as GPIO
import sys


if len(sys.argv) < 2:
    print("Usage: python 4tst.py <camera_url>")
    exit(1)

camera_url = sys.argv[1]
cap = cv2.VideoCapture(camera_url)



# Init LED pin
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)


# Load models
scaler = joblib.load('scaler.pkl')
model = joblib.load('model.pkl')
le = joblib.load('le.pkl')
attendance_file = 'attendance.csv'

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Output file for attendance
attendance_file = 'attendance.csv'

# Confidence threshold for authorization
CONFIDENCE_THRESHOLD = 0.6


def control_led(state):
    GPIO.output(LED_PIN, state)
    print(f"LED turned {'ON' if state else 'OFF'}")


def calculate_angle(hip, knee, ankle):
    v1 = np.array([hip.x - knee.x, hip.y - knee.y])
    v2 = np.array([ankle.x - knee.x, ankle.y - knee.y])
    cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))


stream_url = "http://192.168.235.19:8080/video"
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit(1)

right_angles, left_angles = [], []
WINDOW_SIZE = 60
led_state = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        if all(landmark.visibility > 0.5 for landmark in
               [landmarks[24], landmarks[26], landmarks[28], landmarks[23], landmarks[25], landmarks[27]]):
            right_angle = calculate_angle(
                landmarks[24], landmarks[26], landmarks[28])
            left_angle = calculate_angle(
                landmarks[23], landmarks[25], landmarks[27])
            right_angles.append(right_angle)
            left_angles.append(left_angle)
        else:
            right_angle = left_angle = 0.0

        if len(right_angles) > WINDOW_SIZE:
            right_angles.pop(0)
            left_angles.pop(0)

        if len(right_angles) == WINDOW_SIZE:
            features = np.array([[
                np.mean(right_angles), np.std(right_angles), skew(
                    right_angles), kurtosis(right_angles),
                np.mean(left_angles), np.std(left_angles), skew(
                    left_angles), kurtosis(left_angles)
            ]])
            try:
                # Suppress feature name warning
                features_df = pd.DataFrame(
                    features, columns=scaler.feature_names_in_)
                features_scaled = scaler.transform(features_df)

                predicted_encoded = model.predict(features_scaled)[0]
                confidence = model.predict_proba(features_scaled).max()

                try:
                    predicted_name = le.inverse_transform(
                        [predicted_encoded])[0]
                except ValueError:
                    predicted_name = "Not Identified"
                    confidence = 0.0

                print(
                    f"Features: {features[0]}, Predicted: {predicted_name}, Confidence: {confidence:.2f}")

                new_led_state = predicted_name != "Not Identified"
                if new_led_state != led_state:
                    control_led(new_led_state)
                    led_state = new_led_state

                if predicted_name != "Not Identified":
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
                    attendance_data = {
                        'Video': 'live_feed', 'Name': predicted_name, 'DateTime': current_time}
                    try:
                        if not os.path.exists(attendance_file):
                            attendance_df = pd.DataFrame(
                                columns=['Video', 'Name', 'DateTime'])
                        else:
                            attendance_df = pd.read_csv(attendance_file)
                        attendance_df = pd.concat(
                            [attendance_df, pd.DataFrame([attendance_data])], ignore_index=True)
                        attendance_df.to_csv(
                            attendance_file, index=False, encoding='utf-8-sig')
                        print(f"Updated attendance for {predicted_name}")
                    except Exception as e:
                        print(f"Error saving attendance: {e}")

            except ValueError as ve:
                print(
                    f"Error in prediction (ValueError): {ve}, setting to Not Identified")
                predicted_name = "Not Identified"
                confidence = 0.0
            except Exception as e:
                print(f"Error in prediction: {e}, setting to Not Identified")
                predicted_name = "Not Identified"
                confidence = 0.0

        display_text = f"Predicted: {predicted_name if len(right_angles) == WINDOW_SIZE else 'Processing...'}"
        cv2.putText(frame, display_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("Live Identification", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
control_led(False)
cv2.destroyAllWindows()
pose.close()
print(f"Attendance update process completed. Check {attendance_file}")
