from PyQt5.QtCore import QObject, pyqtSignal


class Worker(QObject):
    finished = pyqtSignal()
    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # print("Worker made")
        self._running = True

    def run(self, value):
        if self._running:
            self.update_signal.emit(value)
        self.finished.emit()

    def stop(self):
        self._running = False
