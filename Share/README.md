# 下載器核心套件
- 給懂得寫程式的人參考。

---

## 模組說明: `async_requests.py`

### 處理非同步請求
#### 1. new_session()
```python
def new_session(
    headers: dict|None=None
    cookies: dict|None=None
) -> ClientSession
```
 - 說明: 回傳一個`aiohttp.ClientSession`物件，用於處理HTTP請求。
 - 參數:
    - `headers`: 標頭，預設會帶有`User-Agent`。
    - `cookies`: Cookies。
 - 回傳值:
    - `aiohttp.ClientSession`物件。
 - 範例:
```python
async def main():
    _client = new_session(
        headers={
            "Range": "byte=0-1024"
        }
    )
    _res = await requests("https://example.com", _client=_client)

    # 新增的Session在使用結束後要記得關掉
    await _client.close()
```

#### 2. await requests()
```python
async def requests(
    url: str,
    _client: ClientSession|None=None,
    *,
    data: Any=None,
    method: "GET"|"POST"|"HEAD"="GET",
    headers: dict|None=None,
    cookies: dict[str, str]|None=None,
    raw: bool=False,
) -> bytes|CIMultiDictProxy|ClientResponse:
```
 - 說明: 視輸入參數回傳不同的值，用於發送HTTP請求。
 - 參數:
    - `url`: 請求網址。
    - `_client`: `aiohttp.ClientSession`物件，若無則會自行使用`new_session`創建，並且在函式結束時關閉。
    - `data`: 要傳送的資料。
    - `method`: 請求方法。
    - `headers`: 標頭，預設會使用`_client`的標頭。
    - `cookies`: Cookies。
    - `raw`: 是否回傳原始回應(`aiohttp.ClientResponse`)
 - 回傳值(依照優先順序):
    - 如果`raw`為`True`:
       - `aiohttp.ClientResponse`
    - 如果`method`為`HEAD`:
       - 回傳`multidict.CIMultiDictProxy`
    - 其他:
       - 回傳`bytes`
 - 範例:
```python
async def main():
    res = await requests("https://example.com", data={"test": "test"}, method="POST", raw=True)
```

---

## 模組說明: `myself.py`
> 以下範例如有關於動畫資訊，皆以`Hello World`(網址:`https://myself-bbs.com/thread-46195-1-1.htmls`)作為範例。

### 影片物件 - `class MyselfAnime`
#### 1. 宣告物件
 - 說明: Myself影片物件
 - 參數: 
    - `episode_name`: 該集名稱(如: `第 01 話`)，任意，不影響下載。
    - `tid`: 動畫ID(如: `46195`)
    - `vid`: 該集ID(如: `001`)
 - 範例:
```python
anime = MyselfAnime("第 01 話", "46195", "001")
```

#### 2. 物件參數
 - `EPS_NAME`: 該集名稱。
 - `TID`: 該動畫ID。
 - `VID`: 該集ID。

#### 3. await MyselfAnime.get_m3u8_url()
```python
async def get_m3u8_url(
    _ws: WebSocketClientProtocol|None=None
) -> tuple[str, str]:
```
 - 說明: 取得該集動畫之.m3u8檔案位置及主機位置。
 - 參數:
    - `_ws`: `websockets.client.WebSocketClientProtocol`物件，若無則會自行創建，並且在函式結束時關閉。
 - 回傳值(依照回傳位置):
    - m3u8主機位置。
    - .m3u8檔案位置。
 - 範例:
```python
async def main():
    anime = MyselfAnime("第 01 話", "46195", "001")
    host, file_path = await anime.get_m3u8_url()
```

### 動畫資料物件 - `class MyselfAnimeTable`
#### 1. 宣告物件
 - 說明: Myself動畫資料物件
 - 參數: 
    - `url`: 網址(如: `https://myself-bbs.com/thread-46195-1-1.html`)
    - `name`: 預命名(如: `Hello World`)，用於抓取列表時預先命名，而不用抓取每一部動畫資料，在使用`await MyselfAnimeTable.update()`後，會被動畫名稱覆蓋。
 - 範例:
```python
anime_table = MyselfAnimeTable("https://myself-bbs.com/thread-46195-1-1.html")
```

#### 2. 物件參數
 - `updated`: 資料是否已更新。
 - -----以下參數需在更新後才可存取-----
 - `URL`: 該集網址。
 - `TID`: 該動畫ID。
 - `NAME`: 動畫名稱。
 - `ANI_TYPE`: 動畫類型(對應Myself頁面中`作品類型`)。
 - `PRE_DATE`: 動畫首播日期(對應Myself頁面中`首播日期`)。
 - `EPS_NUM`: 播放集數(對應Myself頁面中`播出集數`)。
 - `AUTHOR`: 作者(對應Myself頁面中`原著作者`)。
 - `OFFICIAL_WEB`: 官方網站(對應Myself頁面中`官方網站`)。
 - `REMARKS`: 備註(對應Myself頁面中`備注`)。
 - `INTRO`: 簡介(對應Myself頁面中`劇情簡介`)。
 - `IMAGE_URL`: 縮圖連結。
 - `VIDEO_LIST`: `MyselfAnime`物件列表。