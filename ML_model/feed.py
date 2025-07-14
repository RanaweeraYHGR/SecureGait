try:
    import sys
    import cv2
    import mediapipe as mp
    import numpy as np
    import pandas as pd
    import joblib
    import time
    import RPi.GPIO as GPIO
    import os
    import logging
    import traceback

except Exception as e:
    with open('/home/pi/ML_model/feed_crash.log', 'w') as f:
        f.write(f"IMPORT CRASH: {e}\n")
    sys.exit(1)

# Suppress TensorFlow Lite logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Logging setup
logging.basicConfig(
    filename='/home/pi/ML_model/print.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

BASE_DIR = '/home/pi/ML_model'

# Load model/scaler

logging.info("feed.py starting up!")

try:
    model = joblib.load(os.path.join(BASE_DIR, 'model.pkl'))
    scaler = joblib.load(os.path.join(BASE_DIR, 'scaler.pkl'))
    logging.info("Models loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model or scaler: {e}")
    sys.exit(1)

# initializing meadiapip

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

try:
    pose = mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
except Exception as e:
    logging.error(f"Failed to initialize MediaPipe Pose: {str(e)}")


def extract_knee_angles(video_path):
    try:    
        cap = cv2.VideoCapture(video_path)
        left_knee_angles, right_knee_angles = [], []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark

                def get_angle(a, b, c):
                    a = np.array([lm[a].x, lm[a].y])
                    b = np.array([lm[b].x, lm[b].y])
                    c = np.array([lm[c].x, lm[c].y])
                    ba = a - b
                    bc = c - b
                    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
                    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

                visible = all(lm[i].visibility > 0.5 for i in [23, 24, 25, 26, 27, 28])
                if visible:
                    right_knee_angles.append(get_angle(24, 26, 28))
                    left_knee_angles.append(get_angle(23, 25, 27))

        if not right_knee_angles or not left_knee_angles:
            return None

        return {
            'Right_Mean_Angle': np.mean(right_knee_angles),
            'Right_Std_Angle': np.std(right_knee_angles),
            'Right_Skewness': pd.Series(right_knee_angles).skew(),
            'Right_Kurtosis': pd.Series(right_knee_angles).kurt(),
            'Left_Mean_Angle': np.mean(left_knee_angles),
            'Left_Std_Angle': np.std(left_knee_angles),
            'Left_Skewness': pd.Series(left_knee_angles).skew(),
            'Left_Kurtosis': pd.Series(left_knee_angles).kurt()
        }
    
    except Exception as e:
        logging.error(f"Error in extract_knee_angles: {str(e)}")
        return None
    finally:
        cap.release()


def predict(video_path):
    logging.info(f"Starting prediction for {video_path}")

    try:
        features = extract_knee_angles(video_path)

        if features is None:
            logging.warning("No valid pose landmarks found in video.")
            return False

        input_df = pd.DataFrame([features])
        scaled_input = scaler.transform(input_df)
        proba = model.predict_proba(scaled_input)[0]
        max_prob = np.max(proba)
        predicted_name = model.classes_[np.argmax(proba)]

        logging.info(f"Predicted: {predicted_name} with confidence {max_prob:.2f}")

        if max_prob >= 0.4:
            logging.info(f"Identity confirmed: {predicted_name}")
            return predicted_name
        else:
            logging.info("Confidence too low — identity not confirmed.")
            return False

    except Exception as e:
        logging.error("Exception during prediction:\n%s", traceback.format_exc())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("Usage: python yourscript.py <video_file>")
        sys.exit(1)

    video_file = sys.argv[1]
    result = predict(video_file)
    if result:
        print(result)
