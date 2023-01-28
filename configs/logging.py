from .config import LOGGING_CONFIG, MAX_LOGGER_NAME, TIMEZONE

from copy import copy
from logging import Formatter, getLevelName, getLogger, LogRecord, NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL, StreamHandler
from os import fspath, listdir, makedirs, remove, rename
from os.path import abspath, exists, isdir, isfile, join, split, splitext
from datetime import datetime, time, timedelta
from io import TextIOWrapper
from traceback import format_exception

from click import style
from http import HTTPStatus

LEVEL_NAME_COLORS = {
    5: "blue",
    DEBUG: "cyan",
    INFO: "green",
    WARNING: "yellow",
    ERROR: "red",
    CRITICAL: "bright_red"
}

STATSU_CODE_COLORS = {
    1: "cyan",
    2: "green",
    3: "yellow",
    4: "red",
    5: "bright_red",
}


class C_Formatter(Formatter):
    def __init__(self, *args, use_color=False, auto_sep: bool = False, **kwargs) -> None:
        self.use_color = use_color
        self.auto_sep = auto_sep
        super().__init__(*args, **kwargs)

    def __color_level_name(self, level_name: str, level_no: int):
        return style(text=level_name, fg=LEVEL_NAME_COLORS.get(level_no))

    def format(self, record: LogRecord) -> str:
        record = copy(record)
        if "color_message" in record.__dict__ and self.use_color:
            record.msg = record.__dict__["color_message"]
            record.__dict__["message"] = record.getMessage()
        message = record.getMessage()
        sep = " " * (9 - len(record.levelname))
        asctime = datetime.now(TIMEZONE).isoformat(" ")
        name = record.name.split(".", 1)[0]
        if self.auto_sep:
            name += "-" * (MAX_LOGGER_NAME - len(name))
        levelname = self.__color_level_name(
            record.levelname, record.levelno) if self.use_color else record.levelname
        s = f"[{asctime}][{name}][{levelname}]:{sep}{message}"
        if record.exc_info:
            record.exc_text = record.exc_text if record.exc_text else "".join(
                format_exception(*record.exc_info))
        if record.exc_text:
            s += "" if s.endswith("\n") else "\n"
            s += record.exc_text
        if record.stack_info:
            s += "" if s.endswith("\n") else "\n"
            s += record.stack_info
            # from traceback import format_stack
            # s += format_stack(record.stack_info)
        return s


class C_UvicornAccessFormatter(C_Formatter):
    def __get_status_code(self, status_code: int) -> str:
        try:
            status_phrase = HTTPStatus(status_code).phrase
        except ValueError:
            status_phrase = ""
        return style(
            text=f"{status_code} {status_phrase}",
            fg=STATSU_CODE_COLORS.get(status_code // 100)
        )

    def format(self, record: LogRecord) -> str:
        record = copy(record)
        client_addr, method, full_path, http_version, status_code = record.args
        request_line = "%s %s HTTP/%s" % (method, full_path, http_version)
        request_line = style(
            text=request_line, bold=True) if self.use_color else request_line
        status_code = self.__get_status_code(
            int(status_code)) if self.use_color else status_code
        record.args = ()
        record.msg = "%s - \"%s\" %s" % (client_addr,
                                         request_line, status_code)
        return super().format(record=record)


class C_FileHandler(StreamHandler):
    def __init__(self, filename: str, backupCount: int = 0, level=NOTSET):
        self.level = 10
        if not filename.endswith(".log"):
            filename += ".log"
        self.baseFilename = abspath(fspath(filename))
        self.backupCount = backupCount
        self.nextRolloverDay = self._next_rollover()
        super().__init__(stream=self._open())
        self.setFormatter(C_Formatter())
        self.setLevel(level)
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
        if self.backupCount == 0:
            return
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
        for logName in logs[self.backupCount:]:
            remove(join(dirPath, logName))

    def _next_rollover(self) -> datetime:
        _nextRolloverDate = datetime.now(TIMEZONE).date() + timedelta(days=1)
        _zeroTime = time(hour=0, minute=0, second=0)
        return datetime.combine(_nextRolloverDate, _zeroTime, TIMEZONE)

    def __repr__(self) -> str:
        level = getLevelName(self.level)
        return f"<{self.__class__.__name__} {self.baseFilename} ({level})>"


class C_StreamHandler(StreamHandler):
    def __init__(self, *args, level=NOTSET, **kwargs):
        self.level = 10
        super().__init__(*args, **kwargs)
        self.setFormatter(C_Formatter(use_color=True, auto_sep=True))
        self.setLevel(level)


def logger_init():
    for name in LOGGING_CONFIG.keys():
        config = LOGGING_CONFIG[name]
        if not isdir(config.dir_path):
            makedirs(config.dir_path)
        filename = join(config.dir_path, f"{config.file_name}.log")
        logger = getLogger(name)
        logger.setLevel(10)
        logger.handlers = [
            C_FileHandler(
                filename=filename,
                backupCount=config.backup_count,
                level=config.file_level
            ),
            C_StreamHandler(level=config.stream_level)
        ]
        if name == "uvicorn":
            logger.propagate = False
            access_handler = C_StreamHandler(level=config.stream_level)
            access_handler.formatter = C_UvicornAccessFormatter(use_color=True)
            access_file_handler = C_FileHandler(
                filename=filename,
                backupCount=config.backup_count,
                level=config.file_level
            )
            access_file_handler.formatter = C_UvicornAccessFormatter(
                use_color=False)
            logger = getLogger("uvicorn.access")
            logger.handlers = [
                C_FileHandler(
                    filename=filename,
                    backupCount=config.backup_count,
                    level=config.file_level
                ), access_handler
            ]
            logger.propagate = False
    getLogger("main").info("Logging Init.")
