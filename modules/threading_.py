import ctypes
import threading
from time import sleep
from logging import getLogger

logger = getLogger("ThreadManger")

class Thread(threading.Thread):
    """
    可停止式線程。
    新增:
     - stop(): 強制停止線程。
     - get_return(): 取得函數回傳值。
    """
    # def __init__(self, group=None, target=..., name: Optional[str]=None, args: Optional[None]=(), kwargs: Optional[None]={}, *, daemon: Optional[bool]=None) -> None:
    #     self._args = args
    #     self._kwargs = kwargs
    #     super().__init__(group, target, name, args, kwargs, daemon=daemon)
    _return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def get_return(self):
        return self._return

    def stop(self):
        if not self.is_alive() or self.ident == None: raise threading.ThreadError("The thread is not active.")
        elif ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, ctypes.py_object(SystemExit)) == 1: return
        ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def _auto_kill():
    while threading.main_thread().is_alive():
        sleep(0.1)
    logger.warning("Detected main thread was stopped.")
    for _ in range(3):
        for thread in threading.enumerate():
            if thread.ident != threading.current_thread().ident and thread.is_alive():
                logger.warning(f"Try to stop {thread.name} thread.")
                thread.stop()
                thread.join()
    logger.warning("All threads were stopped.")
    threading.current_thread().stop()

_auto_kill_thread = Thread(target=_auto_kill, name="AutoKillThread")
_auto_kill_thread.start()
