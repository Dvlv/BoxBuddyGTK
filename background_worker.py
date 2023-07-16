from threading import Thread


class BackgroundWorker(Thread):
    def __init__(self, func_to_run, callback):
        super().__init__()
        self.callback = callback
        self.func_to_run = func_to_run

    def run(self):
        self.func_to_run()

        self.callback()
