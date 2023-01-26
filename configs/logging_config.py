from .config import *

from logging import Formatter, getLevelName, getLogger, LogRecord, NOTSET, StreamHandler
from os import fspath, listdir, makedirs, remove, rename
from os.path import abspath, exists, isdir, isfile, join, split, splitext
from datetime import datetime, time, timedelta
from io import TextIOWrapper
from traceback import format_exception

class C_Formatter(Formatter):
    def format(self, record: LogRecord) -> str:
        record.message = record.getMessage()
        record.asctime = datetime.now(TIMEZONE).isoformat(" ")
        s = f"[{record.asctime}][{record.name}][{record.levelname}]: {record.message}"
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = format_exception(*record.exc_info)
        if record.exc_text:
            if not s.endswith("\n"): s += "\n"
            s += record.exc_text
        if record.stack_info:
            if not s.endswith("\n"): s += "\n"
            # from traceback import format_stack
            # s += format_stack(record.stack_info)
            s += record.stack_info
        return s

class C_FileHandler(StreamHandler):
    def __init__(self, filename: str, backupCount: int=0):
        if not filename.endswith(".log"):
            filename += ".log"
        self.baseFilename = abspath(fspath(filename))
        self.backupCount = backupCount
        self.nextRolloverDay = self._next_rollover()
        self.level = NOTSET
        super().__init__(stream=self._open())
        self.setFormatter(C_Formatter())
        if isfile(self.baseFilename):
            raw_data = open(self.baseFilename, mode="rb").read()
            if raw_data != b"":
                self.rotate()
    
    def close(self):
        self.acquire()
        if self.stream:
            self.flush()
            self.stream.close()
            self.stream = None
        super().close()
        self.release()
    
    def emit(self, record):
        if self.stream == None:
            self.stream = self._open()
        if self.stream:
            super().emit(record=record)
    
    def should_rollover(self) -> bool:
        if datetime.now(TIMEZONE) >= self.nextRolloverDay:
            self.nextRolloverDay = self._next_rollover()
            return True
        return False
    
    def rotate(self) -> bool:
        self.close()
        rolloverName = self._gen_filename()
        self.acquire()
        if exists(rolloverName):
            raw_data = open(self.baseFilename, mode="rb").read()
            open(rolloverName, mode="ab").write(raw_data)
            remove(self.baseFilename)
        else:
            rename(self.baseFilename, rolloverName)
        self.release()
        self.stream = self._open()
        self.nextRolloverDay = self._next_rollover()
        self._delete_file()
    
    def _open(self) -> TextIOWrapper:
        return open(self.baseFilename, mode="a", encoding="utf-8")
    
    def _gen_filename(self) -> str:
        isoTime = datetime.now(TIMEZONE).replace(microsecond=0).isoformat()
        strTime = isoTime.replace(":", "_")
        fileTitle, _ = splitext(self.baseFilename)
        return f"{fileTitle} {strTime}.log"
    
    def _delete_file(self) -> None:
        if self.backupCount == 0: return
        dirPath, fileName = split(self.baseFilename)
        fileTitle, _ = splitext(fileName)
        fileTitle += " "
        logs = [_fn for _fn in listdir(dirPath) if _fn.startswith(fileTitle)]
        def _sort_time(logName: str):
            logName, _ = splitext(logName)
            strTime = logName.removeprefix(fileTitle)
            isoTime = strTime.replace("_", ":")
            return datetime.fromisoformat(isoTime)
        logs.sort(key=_sort_time, reverse=True)
        for logName in logs[self.backupCount:]: remove(join(dirPath, logName))
    
    def _next_rollover(self) -> datetime:
        _nextRolloverDate = datetime.now(TIMEZONE).date() + timedelta(days=1)
        _zeroTime = time(hour=0, minute=0, second=0)
        return datetime.combine(_nextRolloverDate, _zeroTime, TIMEZONE)

    def __repr__(self) -> str:
        level = getLevelName(self.level)
        return f"<{self.__class__.__name__} {self.baseFilename} ({level})>"

class C_StreamHandler(StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(C_Formatter())

def logger_init():
    for name in LOGGING_CONFIG.keys():
        config = LOGGING_CONFIG[name]
        if not isdir(config.dir_path):
            makedirs(config.dir_path)
        file_name = join(config.dir_path, f"{config.file_name}.log")
        logger = getLogger(name)
        logger.setLevel(10)
        stream_handler = C_StreamHandler()
        stream_handler.setLevel(config.stream_level)
        logger.addHandler(stream_handler)
        file_handler = C_FileHandler(file_name, config.backup_count)
        file_handler.setLevel(config.file_level)
        logger.addHandler(file_handler)
    getLogger("main").info("Logging Init.")
