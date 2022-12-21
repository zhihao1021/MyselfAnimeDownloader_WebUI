from .config import *
from logging import StreamHandler, getLevelName, Formatter, LogRecord, getLogger, NOTSET
from os import fspath, listdir, remove, rename, makedirs
from os.path import abspath, split, splitext, exists, isdir, join
from datetime import datetime, timedelta
from io import TextIOWrapper
from traceback import format_exception, format_stack

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

for name in LOGGING_CONFIG.keys():
    _config = LOGGING_CONFIG[name]
    if not isdir(_config.DIR_PATH):
        makedirs(_config.DIR_PATH)
    _file_name = join(_config.DIR_PATH, f"{_config.FILE_NAME}.log")
    _logger = getLogger(name)
    _logger.setLevel(10)
    _stream_handler = C_StreamHandler()
    _stream_handler.setLevel(_config.STREAM_LEVEL)
    _logger.addHandler(_stream_handler)
    _file_handler = C_FileHandler(_file_name, _config.BACKUP_COUNT)
    _file_handler.setLevel(_config.FILE_LEVEL)
    _logger.addHandler(_file_handler)

MAIN_LOGGER = getLogger("main")
WEB_LOGGER = getLogger("web")
