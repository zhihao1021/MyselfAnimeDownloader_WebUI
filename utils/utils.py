BAN_TABLE = str.maketrans("\\/:*?\"<>|", " "*10)
BAN_TABLE.update({i: chr(i) for i in range(32)})

def retouch_name(name: str) -> str:
    """
    避免不正當名字出現導致資料夾或檔案無法創建。
    name: :class:`str`
        輸入字串。

    return: :class:`str`
        修飾後字串。
    """
    return name.translate(BAN_TABLE).strip()