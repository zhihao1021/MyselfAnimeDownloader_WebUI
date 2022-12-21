from typing import Any, Optional, Union

import orjson

class Json:
    """
    基於orjson的改良版本。
    """
    @staticmethod
    def dumps(data: Any,
        option: Optional[int]=None
    ) -> str:
        """
        將`data`轉換為字串。
        
        data: :class:`Any`
            輸入資料。
        option: :class:`int`
            orjson選項。

        return: :class:`str`
        """
        if option != None: return orjson.dumps(data, option=option).decode('utf-8')
        return orjson.dumps(data).decode('utf-8')

    @staticmethod
    def loads(data: Union[bytes, bytearray, memoryview, str]) -> Any:
        """
        將`data`轉換為資料。
        
        data: :class:`bytes | bytearray | memoryview | str`
            輸入文字。

        return: :class:`Any`
        """
        return orjson.loads(data)

    @staticmethod
    def dump(
        file: str,
        data: Any,
        option: int = orjson.OPT_INDENT_2
    ) -> None:
        """
        將`data`儲存於`file`中。
        
        file: :class:`str`
            文件路徑。
        data: :class:`Any`
            輸入資料。
        option: :class:`int`
            orjson選項。

        return: :class:`None`
        """
        with open(file, mode='wb') as in_file:
            in_file.write(orjson.dumps(data, option=option))
            in_file.close()

    @staticmethod
    def load(file: str) -> Any:
        """
        從`file`中讀取資料。
        
        file: :class:`str`
            文件路徑。

        return: :class:`Any`
        """
        with open(file, mode='rb') as in_file:
            data = in_file.read()
            in_file.close()
        return orjson.loads(data.decode("utf-8"))
