import serial
import threading
import time
from config import SERIAL_PORT, BAUD_RATE

class SerialReader:
    """
    Before:
    The SerialReader class was designed to read from the serial port in a separate
    thread. However, the read_serial_data method had a very short sleep time (0.01s),
    which could lead to high CPU usage. The method also contained complex logic for
    debouncing, which could be simplified.
    """
    def __init__(self, debounce_time=0.05):
        self.ser = None
        self.running = False
        self.reset_request = False
        
        # State for handling button presses
        self.key_states = [False] * 4
        self.last_key_states = [False] * 4
        
        # Debouncing variables
        self.debounce_time = debounce_time
        self.last_press_time = [0] * 4

    def start(self):
        """
        Initializes and starts the serial reading thread.
        """
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01)
            self.running = True
            self.thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.thread.start()
            print(f"Serial port {SERIAL_PORT} opened successfully.")
        except serial.SerialException:
            print(f"Failed to open serial port {SERIAL_PORT}.")
            self.ser = None

    def stop(self):
        """
        Stops the serial reading thread and closes the serial port.
        """
        self.running = False
        if self.thread:
            self.thread.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Serial port {SERIAL_PORT} closed.")

    def read_serial_data(self):
        """
        After:
        The read_serial_data method has been optimized to reduce CPU usage. The
        sleep time has been increased to 0.02s, which is a better balance between
        responsiveness and performance. The debouncing logic has been simplified
        to be more efficient.
        """
        while self.running:
            if not self.ser:
                time.sleep(0.1)
                continue

            # Read from serial
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    
                    if line == "RESET":
                        self.reset_request = True
                    elif line.isdigit():
                        key_index = int(line)
                        if 0 <= key_index < 4:
                            self.key_states[key_index] = True
                            self.last_press_time[key_index] = time.time()
            except (serial.SerialException, IOError, ValueError):
                print("Error reading from serial port.")
                self.ser = None
                continue

            # Debounce and update key states
            now = time.time()
            for i in range(4):
                if self.key_states[i] and (now - self.last_press_time[i] > self.debounce_time):
                    self.key_states[i] = False

            time.sleep(0.02) # Increased sleep time to reduce CPU usage

    def get_key_states(self):
        """
        Returns the current state of all keys (True for pressed, False for released).
        """
        return self.key_states

    def get_key_presses(self):
        """
        Returns a list of keys that have been pressed since the last call.
        This ensures that a single press event is only registered once.
        """
        pressed_keys = []
        for i in range(4):
            if self.key_states[i] and not self.last_key_states[i]:
                pressed_keys.append(i)
        
        self.last_key_states = list(self.key_states)
        return pressed_keys

    def get_reset_request(self):
        """
        Checks if a reset request has been received.
        """
        if self.reset_request:
            self.reset_request = False
            return True
        return False