from typing import Union

BAN_TABLE = {
    i: " "
    for i in b"\\/:*?\"<>|" + bytes(range(32))
}

BAN_PATH_TABLE = {
    i: " "
    for i in b":*?\"<>|" + bytes(range(32))
}


def retouch_name(name: Union[str, bytes]) -> Union[str, bytes]:
    """
    避免不正當名字出現導致資料夾或檔案無法創建。
    name: :class:`str`
        輸入字串。

    return: :class:`str`
        修飾後字串。
    """
    if type(name) == str:
        return name.translate(BAN_TABLE).strip()
    return name.decode().translate(BAN_TABLE).strip().encode()


def retouch_path(path: Union[str, bytes]) -> Union[str, bytes]:
    """
    避免不正當名字出現導致路徑錯誤。
    path: :class:`str`
        輸入字串。

    return: :class:`str`
        修飾後字串。
    """
    if type(path) == str:
        return path.translate(BAN_PATH_TABLE).strip()
    return path.decode().translate(BAN_PATH_TABLE).strip().encode()
