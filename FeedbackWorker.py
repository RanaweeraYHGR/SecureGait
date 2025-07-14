import RPi.GPIO as GPIO
import threading
import time
import logging
import queue

class FeedbackWorker(threading.Thread):
    def __init__(self,
                 feedback_queue,
                 CMD_OK, CMD_NOT_A, CMD_NOT_B,
                 blink_led_loop,
                 buzzer_a_loop,
                 buzzer_b_loop,
                 pin18, pin22,pin26, buzzer_pin):
        super().__init__()
        self.queue = feedback_queue
        self.CMD_OK = CMD_OK
        self.CMD_NOT_A = CMD_NOT_A
        self.CMD_NOT_B = CMD_NOT_B
        self.blink_not_led_loop = blink_led_loop
        self.buzzer_sound_type_a_loop = buzzer_a_loop
        self.buzzer_sound_type_b_loop = buzzer_b_loop
        self.PIN18 = pin18
        self.PIN22 = pin22
        self.PIN26 = pin26
        self.BUZZER_PIN = buzzer_pin
        self.stop_event = threading.Event()

    def run(self):
        logging.info("FeedbackWorker started")
        while not self.stop_event.is_set():
            try:
                command = self.queue.get(timeout=0.5)
                logging.info(f"FeedbackWorker got command: {command}")

                if command == self.CMD_OK:
                    self.play_ok()
                elif command == self.CMD_NOT_A:
                    self.play_not_a()
                elif command == self.CMD_NOT_B:
                    self.play_not_b()
                else:
                    logging.warning(f"Unknown command: {command}")

            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"FeedbackWorker error in run loop: {e}")

        logging.info("FeedbackWorker exiting")

    def stop(self):
        self.stop_event.set()

    def play_ok(self):
        logging.info("Playing OK signal")
        GPIO.output(self.PIN18, True)
        GPIO.output(self.PIN26,True)
        time.sleep(2)
        GPIO.output(self.PIN18, False)
        GPIO.output(self.PIN26,False)

    def play_not_a(self):
        logging.info("Playing NOT_A signal (buzzer A loop)")
        self.run_led_and_buzzer_loop(
            self.blink_not_led_loop,
            self.buzzer_sound_type_a_loop
        )

    def play_not_b(self):
        logging.info("Playing NOT_B signal (buzzer B loop)")
        self.run_led_and_buzzer_loop(
            self.blink_not_led_loop,
            self.buzzer_sound_type_b_loop
        )

    def run_led_and_buzzer_loop(self, led_func, buzzer_func, duration=5):
        stop_event = threading.Event()

        led_thread = threading.Thread(target=led_func, args=(stop_event,))
        buzzer_thread = threading.Thread(target=buzzer_func, args=(stop_event,))

        led_thread.start()
        buzzer_thread.start()

        time.sleep(duration)

        stop_event.set()
        led_thread.join()
        buzzer_thread.join()

        GPIO.output(self.BUZZER_PIN, GPIO.LOW)
        GPIO.output(self.PIN22, GPIO.LOW)
