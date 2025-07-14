import threading
import time
import subprocess
import RPi.GPIO as GPIO

class CameraMonitor:
    def __init__(self, camera_url, led_pin=10, check_interval=2):
        self.CAMERA_URL = camera_url
        self.LED_PIN = led_pin
        self.CHECK_INTERVAL = check_interval
        self.camera_ok = False
        self._running = False

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        GPIO.output(self.LED_PIN, False)

    def _check_camera(self):
        """Lightweight camera status check"""
        try:
            result = subprocess.run(
                ['curl', '-sSf', '--max-time', '3', self.CAMERA_URL],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            self.camera_ok = (result.returncode == 0)
            GPIO.output(self.LED_PIN, self.camera_ok)  # Update LED immediately
            return self.camera_ok
        except:
            self.camera_ok = False
            GPIO.output(self.LED_PIN, False)
            return False

    def _monitor_loop(self):
        """Continuous camera checking thread"""
        while self._running:
            self._check_camera()
            time.sleep(self.CHECK_INTERVAL)

    def start(self):
        """Start background monitoring"""
        if not self._running:
            self._running = True
            threading.Thread(target=self._monitor_loop, daemon=True).start()

    def stop(self):
        """Stop monitoring and cleanup"""
        self._running = False
        GPIO.output(self.LED_PIN, False)

    def status(self):
        """Get current camera status"""
        return {
            'ok': self.camera_ok,
            'last_check': time.time()
        }