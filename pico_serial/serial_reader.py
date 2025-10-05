import serial
import threading
import queue

class SerialReader:
    def __init__(self, port="COM3", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.q = queue.Queue()
        self.running = False
        self.thread = None
        self.ser = None

    def start(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def _read_loop(self):
        while self.running:
            try:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    self.q.put(line)
            except Exception as e:
                self.q.put(f"[Błąd seriala: {e}]")
                self.running = False

    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()

    def get_line(self):
        try:
            return self.q.get_nowait()
        except queue.Empty:
            return None
