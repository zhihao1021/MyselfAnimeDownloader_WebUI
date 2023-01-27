from utils import Json

from copy import deepcopy
from datetime import timedelta, timezone, time
from logging import getLevelName
from os import makedirs
from os.path import abspath, isdir, isfile
from pydantic import BaseModel, Field, validator
from sqlite3 import connect
from typing import Union, Optional

def __recursion_update(old_dict: dict, new_dict: dict) -> dict:
    """
    遞迴更新字典。
    """
    for key, value in new_dict.items():
        if type(value) == dict:
            old_value = old_dict.get(key, {})
            old_value = __recursion_update(old_value, value)
            old_dict[key] = old_value
        else:
            old_dict[key] = value
    return old_dict

def path_validator(path: str):
    if not isdir(path := abspath(path)):
        makedirs(path)
    return path

# CRITICAL
# ERROR
# WARNING
# INFO
# DEBUG
# NOTSET
class LoggingConfig(BaseModel):
    stream_level: Union[int, str]=Field(20, alias="stream-level")
    file_level: Union[int, str]=Field(20, alias="file-level")
    backup_count: int=Field(3, alias="backup-count", ge=0)
    file_name: str=Field(alias="file-name")
    dir_path: str=Field("logs", alias="dir-path")

    @validator("stream_level", "file_level")
    def level_name_validator(cls, value):
        if value if type(value) == int else getLevelName(value) in range(0, 51, 10):
            return value
        raise ValueError(f"Illegal level name: \"{value}\"")
    
    @validator("dir_path")
    def path_validator(cls, value):
        return path_validator(value)
    
    class Config:
        extra = "ignore"

class WebConfig(BaseModel):
    host: str=Field("0.0.0.0")
    port: int=Field(5000)

class GlobalConfig(BaseModel):
    user_agent: str=Field(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0 (Edition GX-CN)",
        alias="user-agent",
    )
    connections: int=Field(10, ge=1)
    worker: int=Field(3, ge=1)
    retry: int=Field(3, ge=0)
    timeout: float=Field(5, ge=0)
    temp_path: str=Field("temp", alias="temp-path")
    
    @validator("temp_path")
    def path_validator(cls, value):
        return path_validator(value)

class MyselfConfig(BaseModel):
    check_update: int=Field(5, ge=0)
    classify: bool=Field(True)
    file_name: str=Field("[Myself]$NAME $EPS", alias="file-name")
    dir_name: str=Field("[Myself]$NAME", alias="dir-name")
    download_path: str=Field("download/myself", alias="download-path")

    @validator("download_path")
    def path_validator(cls, value):
        return path_validator(value)

EXAMPLE_CONFIG: dict[str, Union[dict, str, int]] = {
    "web": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": False
    },
    "global": {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0 (Edition GX-CN)",
        "connections": 10,
        "threads": 5,
        "retry": 3,
        "timeout": 5,
        "temp-path": "temp",
        "zerofill": 2
    },
    "myself": {
        "check-update": 5,
        "classify": True,
        "file-name": "[Myself]$NAME $EPS",
        "dir-name": "[Myself]$NAME",
        "download-path": "download/myself"
    },
    "logging": {
        "main": {
            "stream-level": "INFO",
            "file-level": "INFO",
            "backup-count": 10,
            "file-name": "web",
            "dir-path": "logs"
        },
        "myself": {
            "stream-level": "INFO",
            "file-level": "INFO",
            "backup-count": 10,
            "file-name": "web",
            "dir-path": "logs"
        },
        "web": {
            "stream-level": "INFO",
            "file-level": "INFO",
            "backup-count": 10,
            "file-name": "web",
            "dir-path": "logs"
        }
    },
    "timezone": 8,
    "ffmpeg-args": ""
}
CONFIG: dict[str, Union[dict, str, int]] = ...

# 更新資料
try:
    config = Json.load_nowait("config.json")
except:
    config = deepcopy(EXAMPLE_CONFIG)
CONFIG = __recursion_update(EXAMPLE_CONFIG, config)
Json.dump_nowait("config.json", CONFIG)

WEB_CONFIG = WebConfig(**CONFIG["web"])
GLOBAL_CONFIG = GlobalConfig(**CONFIG["global"])
MYSELF_CONFIG = MyselfConfig(**CONFIG["myself"])

LOGGING_CONFIG: dict[str, LoggingConfig] = {
    key: LoggingConfig(**value)
    for key, value in CONFIG["logging"].items()
}

TIMEZONE: timezone = timezone(timedelta(hours=CONFIG["timezone"]))
FFMPEG_ARGS = CONFIG["ffmpeg-args"]

MYSELF_URL = "https://myself-bbs.com/"
BS_FEATURE = "html.parser"

with connect("data.db") as db:
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type=\"table\";")
    table_list = map(lambda tup: tup[0], cursor.fetchall())
    if "cache" not in table_list:
        cursor.execute("""
            CREATE TABLE "cache" (
                "url"    TEXT NOT NULL UNIQUE,
                "update_time"    TEXT NOT NULL DEFAULT '1970-01-01T00:00:00',
                PRIMARY KEY("url")
            );
        """)
