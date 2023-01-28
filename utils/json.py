from typing import Any, Optional, Union

from aiofiles import open as aopen

import orjson
from pydantic import BaseModel

def decode_data(by_alias: bool=True, **kwargs):
    def __decode_data(value: Union[BaseModel, Any]):
        if issubclass(type(value), BaseModel):
            return value.dict(by_alias=by_alias, **kwargs)
        return value
    return __decode_data

class Json:
    """
    基於orjson的改良版本。
    """
    @staticmethod
    def dumps(
        data: Any,
        option: Optional[int]=None,
        by_alias: bool=True,
        **kwargs,
    ) -> str:
        """
        將`data`轉換為字串。
        
        :param data: 輸入資料。
        :param option: orjson選項。
        :param by_alias: pydantic選項。
        """
        return orjson.dumps(
            data,
            default=decode_data(by_alias=by_alias, **kwargs),
            option=option
        ).decode('utf-8')

    @staticmethod
    def loads(data: Union[bytes, bytearray, memoryview, str]) -> Any:
        """
        將`data`轉換為資料。
        
        :param data: 輸入文字。
        """
        return orjson.loads(data)
    
    @staticmethod
    async def dump(
        file: str,
        data: Any,
        option: Optional[int]=orjson.OPT_INDENT_2,
        by_alias: bool=True,
        **kwargs
    ) -> None:
        """
        將`data`儲存於`file`中。
        
        :param file: 文件路徑。
        :param data: 輸入資料。
        :param option: orjson選項。
        """
        async with aopen(file, mode="wb") as open_file:
            await open_file.write(orjson.dumps(
                data,
                default=decode_data(by_alias=by_alias, **kwargs),
                option=option
            ))
    
    @staticmethod
    def dump_nowait(
        file: str,
        data: Any,
        option: Optional[int]=orjson.OPT_INDENT_2,
        by_alias: bool=True,
        **kwargs,
    ) -> None:
        """
        將`data`儲存於`file`中。
        
        :param file: 文件路徑 | IOBase Object。
        :param data: 輸入資料。
        :param option: orjson選項。
        """
        with open(file, mode="wb") as open_file:
            open_file.write(orjson.dumps(
                data,
                default=decode_data(by_alias=by_alias, **kwargs),
                option=option
            ))

    @staticmethod
    async def load(file: str) -> Any:
        """
        從`file`中讀取資料。
        
        :param file: 文件路徑。
        """
        async with aopen(file, mode="rb") as open_file:
            return orjson.loads(await open_file.read())
    
    @staticmethod
    def load_nowait(file: str) -> Any:
        """
        從`file`中讀取資料。
        
        :param file: 文件路徑。
        """
        with open(file, mode="rb") as open_file:
            return orjson.loads(open_file.read())
