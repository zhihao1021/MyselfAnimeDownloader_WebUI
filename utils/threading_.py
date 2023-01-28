from ctypes import pythonapi, py_object
from threading import current_thread, enumerate as thread_enumerate, main_thread, Thread as OThread, ThreadError
from time import sleep
from logging import getLogger

logger = getLogger("main")


class Thread(OThread):
    """
    可停止式線程。
    新增:
     - stop(): 強制停止線程。
    """

    def stop(self):
        if not self.is_alive() or self.ident == None:
            raise ThreadError("The thread is not active.")
        elif pythonapi.PyThreadState_SetAsyncExc(self.ident, py_object(SystemExit)) == 1:
            return
        pythonapi.PyThreadState_SetAsyncExc(self.ident, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def __auto_kill():
    while main_thread().is_alive():
        sleep(0.1)
    logger.warning("Detected main thread was stopped.")
    for _ in range(3):
        for thread in thread_enumerate():
            if thread.ident != current_thread().ident and thread.is_alive():
                logger.warning(f"Try to stop {thread.name} thread.")
                if hasattr(thread, "stop"):
                    thread.stop()
                else:
                    if not thread.is_alive() or thread.ident == None:
                        continue
                    pythonapi.PyThreadState_SetAsyncExc(
                        thread.ident, py_object(SystemExit))
                thread.join()
    logger.warning("All threads were stopped.")
    current_thread().stop()


__auto_kill_thread = Thread(target=__auto_kill, name="AutoKillThread")
__auto_kill_thread.start()
