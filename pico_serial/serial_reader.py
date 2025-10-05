import serial
import threading
import queue


class SerialReader:
    """Background serial reader that continuously polls data from the Pico."""

    def __init__(self, port="COM3", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.q = queue.Queue()
        self.running = False
        self.thread = None
        self.ser = None

    # ------------------------------------------------------------------

    def start(self):
        """Open the serial port and start the background reading thread."""
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
            self.ser.close()

    # ------------------------------------------------------------------

    def get_line(self):
        """Return the next line from the queue, or None if no data is available."""
        try:
            return self.q.get_nowait()
        except queue.Empty:
            return None
