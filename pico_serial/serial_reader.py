import serial
import threading
import queue
from serial.tools import list_ports


class SerialReader:
    """Background serial reader that continuously polls data from the Pico."""

    def __init__(self, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.q = queue.Queue()
        self.running = False
        self.thread = None
        self.ser = None

    # ------------------------------------------------------------------

    @staticmethod
    def list_available_ports():
        """Return a list of detected serial port device names."""
        return [port.device for port in list_ports.comports()]

    # ------------------------------------------------------------------

    def is_connected(self):
        """Return True when the serial port is currently open."""
        return bool(self.ser and self.ser.is_open and self.running)

    # ------------------------------------------------------------------

    def start(self, port=None):
        """Open the serial port and start the background reading thread."""
        if port is not None:
            self.port = port
        if not self.port:
            raise ValueError("No serial port selected.")
        if self.is_connected():
            return

        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    # ------------------------------------------------------------------

    def _read_loop(self):
        """Continuously read lines from the serial port and push them to the queue."""
        while self.running:
            try:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    self.q.put(line)
            except Exception as e:
                self.q.put(f"[Serial error: {e}]")
                self.running = False

    # ------------------------------------------------------------------

    def stop(self):
        """Stop reading and close the serial port."""
        self.running = False
        if self.ser:
            try:
                if self.ser.is_open:
                    self.ser.close()
            finally:
                self.ser = None
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        self.thread = None

    # ------------------------------------------------------------------

    def get_line(self):
        """Return the next line from the queue, or None if no data is available."""
        try:
            return self.q.get_nowait()
        except queue.Empty:
            return None
