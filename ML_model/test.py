import queue
import RPi.GPIO as GPIO
import time
import subprocess
import os
from datetime import datetime
import logging
from cameraMonitor import CameraMonitor  # The simplified version
import firebase_admin
from firebase_admin import credentials, firestore
import threading
from datetime import datetime
from FeedbackWorker import FeedbackWorker
import queue
# Firebase setup
cred = credentials.Certificate('/home/pi/ML_model/firebase-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Configuration
IP_CAMERA_URL = "http://192.168.156.92:8080/"
VIDEOS_DIR = "/home/pi/myVideos"
FEED_SCRIPT = "/home/pi/ML_model/feed.py"
SIGNAL_PIN = 17  # Motion sensor GPIO pin
LED_PIN = 10     # Status LED GPIO pin
PIN23 = 23       # Output pin for blinking status
FAN_PIN = 24  # Fan pin
PIN18 = 18  # Blue LED ok signal
PIN22 = 22  # Green LED not ok signal
BUZZER_PIN = 27
SERVER_PIN=26

# Setup logging
logging.basicConfig(
    filename='/home/pi/ML_model/print.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN23, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.output(FAN_PIN, GPIO.LOW)
GPIO.setup(PIN18, GPIO.OUT)
GPIO.setup(PIN22, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(SERVER_PIN,GPIO.OUT)


# ---------- Blinking Utility ----------
def blink_pattern(stop_event, on_off_times):
    """Blink the LED on PIN23 in the given on/off pattern while stop_event is not set."""
    while not stop_event.is_set():
        for duration in on_off_times:
            GPIO.output(PIN23, not GPIO.input(PIN23))
            time.sleep(duration)
            if stop_event.is_set():
                break
    GPIO.output(PIN23, False)  # Ensure LED off at the end


def blink_solid_on(stop_event):
    """Keep the LED on solid while stop_event is not set."""
    GPIO.output(PIN23, True)
    stop_event.wait()
    GPIO.output(PIN23, False)


# ---------- Blinking Modes ----------
def rec_signal(stop_event):
    blink_pattern(stop_event, [0.2, 0.3])


def analizing_signal(stop_event):
    blink_pattern(stop_event, [0.15, 0.15, 0.15, 0.15, 0.15, 1.5])


def db_signal(stop_event):
    blink_solid_on(stop_event)


# --------analized output signals---------\

def blink_ok_led():
    GPIO.output(PIN18, True)
    time.sleep(2)
    GPIO.output(PIN18, False)


def blink_not_led_loop(stop_event):
    while not stop_event.is_set():
        GPIO.output(PIN22, True)
        time.sleep(0.2)
        GPIO.output(PIN22, False)
        time.sleep(0.2)


# ------ buzzer ----------
def buzzer_sound_type_a_loop(stop_event):
    while not stop_event.is_set():
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.5)


def buzzer_sound_type_b_loop(stop_event):
    while not stop_event.is_set():
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
    else:
        GPIO.output(BUZZER_PIN, GPIO.LOW)


def run_led_and_buzzer(led_func, buzzer_func, duration=5):
    stop_event = threading.Event()

    led_thread = threading.Thread(target=led_func, args=(stop_event,))
    buzzer_thread = threading.Thread(target=buzzer_func, args=(stop_event,))

    led_thread.start()
    buzzer_thread.start()

    time.sleep(duration)

    stop_event.set()
    led_thread.join()
    buzzer_thread.join()

    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.output(PIN22, GPIO.LOW)


# ---------- Video Recording ----------
def record_video(video_path):
    """Record 10-second video using FFmpeg while blinking in recording mode."""
    stop_event = threading.Event()
    blink_thread = threading.Thread(target=rec_signal, args=(stop_event,))
    blink_thread.start()

    try:
        result = subprocess.run(
            [
                'ffmpeg',
                '-y',               # Overwrite
                '-i', IP_CAMERA_URL+'/video',
                '-t', '5',         # Duration
                '-c:v', 'copy',     # Stream copy
                '-f', 'mp4',        # Force MP4
                video_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        return result.returncode == 0

    except Exception as e:
        logging.error(f"Recording failed: {str(e)}")
        return False

    finally:
        stop_event.set()
        blink_thread.join()
        GPIO.output(LED_PIN, False)


# ---------- Database Upload ----------
def save_to_database(name):
    stop_event = threading.Event()
    blink_thread = threading.Thread(target=db_signal, args=(stop_event,))
    blink_thread.start()

    try:
        timestamp = datetime.now().isoformat()
        doc_ref = db.collection('detections').document()
        doc_ref.set({
            'name': name,
            'timestamp': timestamp
        })
        logging.info(f"Saved to Firebase: {name}")

    except Exception as e:
        logging.error(f"Error saving to Firebase: {e}")

    finally:
        stop_event.set()
        blink_thread.join()
        GPIO.output(LED_PIN, False)

# -----------check user active or not----------------


def is_user_active(name):
    try:
        # First try to match 'name' field
        query = db.collection('userprofile').where('name', '==', name).limit(1)
        results = query.get()
        if results:
            user_data = results[0].to_dict()
            # Default to True if no 'active' field
            return user_data.get('active', True)

        # If no match on 'name', try 'nickname'
        query = db.collection('userprofile').where(
            'nickname', '==', name).limit(1)
        results = query.get()
        if results:
            user_data = results[0].to_dict()
            # Default to True if no 'active' field
            return user_data.get('active', True)

        # If no user found at all, treat as inactive
        logging.warning(f"No user profile found with name or nickname: {name}")
        return False

    except Exception as e:
        logging.error(f"Error checking user active status: {e}")
        return False  # On error, skip saving to DB


# -----------read raspberry temperature-----------
def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_str = f.readline()
        return float(temp_str) / 1000.0
    except Exception as e:
        logging.error(f"Failed to read CPU temperature: {e}")
        return 0


def monitor_temperature(stop_event):
    FAN_ON = False
    while not stop_event.is_set():
        temp = get_cpu_temp()

        if temp > 45 and not FAN_ON:
            GPIO.output(FAN_PIN, GPIO.HIGH)
            FAN_ON = True
            logging.info("Fan turned ON")

        elif temp < 35 and FAN_ON:
            GPIO.output(FAN_PIN, GPIO.LOW)
            FAN_ON = False
            logging.info("Fan turned OFF")

        time.sleep(5)  # Check every 5 seconds


# ------------------- worker ------------------------
# command for worker
CMD_OK = "ok"
CMD_NOT_A = "not_a"
CMD_NOT_B = "not_b"

feedback_queue = queue.Queue()


# ---------- Main Loop ----------
def main():
    try:
        # Initialize hardware
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SIGNAL_PIN, GPIO.IN)
        os.makedirs(VIDEOS_DIR, exist_ok=True)

        # Start camera monitoring (LED will auto-update)
        monitor = CameraMonitor(IP_CAMERA_URL, LED_PIN)
        monitor.start()
        logging.info("System started - Camera monitor running")

        while True:
            if GPIO.input(SIGNAL_PIN):
                if not monitor.status()['ok']:
                    logging.warning("Camera not ready - skipping capture")
                    time.sleep(1)
                    continue

                # Record video
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_file = f"{VIDEOS_DIR}/video_{timestamp}.mp4"
                logging.info(f"Starting recording: {video_file}")

                if record_video(video_file):
                    # Blinking during analysis
                    stop_event = threading.Event()
                    blink_thread = threading.Thread(
                        target=analizing_signal, args=(stop_event,))
                    blink_thread.start()

                    predicted_name = None
                    result = None

                    try:
                        feed_python = "/home/pi/ML_model/mp-env/bin/python"
                        result = subprocess.run(
                            [feed_python, FEED_SCRIPT, video_file],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            timeout=120
                        )
                        predicted_name = result.stdout.strip()

                    except Exception as e:
                        logging.error(f"Analysis failed: {str(e)}")

                    finally:                
                        stop_event.set()
                        blink_thread.join()
                        GPIO.output(LED_PIN, False)

                        if predicted_name:
                            logging.info(f"Person detected: {predicted_name}")
                            if is_user_active(predicted_name):
                                feedback_queue.put(CMD_OK)
                                save_to_database(predicted_name)
                            else:
                                feedback_queue.put(CMD_NOT_B)
                                logging.info(
                                    f"User {predicted_name} is inactive. Skipping database save.")
                        else:
                            feedback_queue.put(CMD_NOT_A)
                            logging.info(f"Analysis result: {result}")

                        try:
                            os.remove(video_file)
                            logging.info("Video removed")
                        except Exception as e:
                            logging.error(f"Failed to remove video: {str(e)}")

                else:
                    logging.error("Recording failed")

            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("Shutdown requested")

    finally:
        monitor.stop()
        GPIO.cleanup()
        logging.info("System stopped")


if __name__ == '__main__':
    # Start temperature monitoring in a thread
    temp_stop_event = threading.Event()
    temp_thread = threading.Thread(
        target=monitor_temperature, args=(temp_stop_event,))
    temp_thread.start()

    feedback_worker = FeedbackWorker(
        feedback_queue,
        CMD_OK, CMD_NOT_A, CMD_NOT_B,
        blink_not_led_loop,
        buzzer_sound_type_a_loop,
        buzzer_sound_type_b_loop,
        PIN18, PIN22,SERVER_PIN, BUZZER_PIN
    )
    feedback_worker.start()

    main()

    feedback_worker.stop()
