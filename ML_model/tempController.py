import RPi.GPIO as GPIO
import time

FAN_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.output(FAN_PIN, GPIO.LOW)

def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        return float(f.readline()) / 1000.0

try:
    while True:
        temp = get_cpu_temp()
        print(f"Temp: {temp}°C")

        if temp > 10:
            GPIO.output(FAN_PIN, GPIO.HIGH)
        elif temp < 5:
            GPIO.output(FAN_PIN, GPIO.LOW)

        time.sleep(5)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
