# 開發日誌
### MyselfAnimeDownloader WebUI開發日誌，最後更新日期`2023/02/07`
---

<style>
    p {
        text-indent: 2em;
    }
</style>

## TODO Summary
> 詳細下一次做甚麼會寫在每次更新的日誌中

1.  ~~新增單元測試(Unit Testing)~~ 2023/02/20 放棄
2.  ~~新增m3u8下載器~~ 2022/12/28
3.  ~~移植Web UI~~ 2023/01/12
4.  ~~後端重構~~ 2023/01/12
5.  連結SQL Database紀錄下載
6.  ~~新增貯列管理器~~ 2023/01/01
7.  ~~WebSocket Server~~ 2023/02/20
8.  行動版專有頁面(放棄做RWD了XD
9.  ~~Read From Cache~~ 2023/01/10
10. ~~自訂介面色彩~~ 2023/01/11
11. 定時檢查動畫更新
12. ~~框架改FastAPI~~ 2023/01/28
13. ~~通知氣泡~~ 2023/02/26

---

## 2023/02/26
```
---Log---
1. 通知氣泡完成

--TODO Detal---
1. WebUI自動檢查更新設定
```

---

## 2023/02/20
```
---Log---
1. 下載清單的API改為使用WebSocket。
2. 新增自動檢查更新雛形。
3. WebUI所有完結列表部分，改為只有在顯示時才會請求資源。
4. WebUI中，啟用設定功能。

--TODO Detal---
1. WebUI自動檢查更新設定
2. 通知氣泡(開始下載、下載完成...)
```

---

## 2023/02/07
```
---Log---
1. 修正requests函式例外處理Logger位置。
2. 關閉SSL驗證，避免部分電腦發生憑證錯誤。
3. 棄用websockets套件，改為aiohttp附帶之WebSocket。

--TODO Detal---
1. 自動檢查更新
```

---

## 2023/01/28
```
---Log---
1. 將框架改為FastAPI。
2. 修正快取問題。

---TODO Detail---
1. 自動檢查更新
```

---

## 2023/01/27
```
---Log---
1. 資料結構改為Pydantic。
2. 快取棄用Database紀錄修改時間，改為直接讀取檔案修改時間。
3. 語法優化。
4. 修改註解。

---TODO Detail---
1. 框架改為FastAPI
```

---

## 2023/01/12
```
---Log---
1. 自訂介面色彩完成。
2. 新增刷新頁面按鈕(從伺服器而非快取存取資訊)。
3. 更新dashboard.py中asyncio loop回收。
4. Web UI完結動畫列表完成。

```

---

## 2023/01/10
```
---Log---
1. 修正Web UI動畫資料顯示問題。
2. 修正Myself Method中search語法錯誤(CSS Selector)。
3. M3U8下載失誤自動修正新增檢查條件-檔案完整度。
4. Web UI每周列表完成。
5. Web UI年表完成。
6. Read From Cache完成。

---TODO Detail---
1. Web UI自訂色彩
2. Web UI完結動畫列表
3. 定時檢查動畫更新
```

---

## 2023/01/08
```
---Log---
1. 修正Myself method中finish_list與search運行邏輯。
2. 修正M3U8.py中gen_dir_name函式變數誤植。
3. Web UI搜尋列表完成。
4. Web UI動畫資料頁完成。
5. Web UI設定頁完成。
6. Web UI搜尋功能完成。
7. Web UI下載功能完成完成。
8. Web UI貯列操作完成。
9. 將原本於Dashboard中API單獨拉出來做為一個Module，方便日後其他介面使用。

# 基本上算是能用了

---TODO Detail---
1. Web UI網頁播放器
2. Web UI每周更新列表
3. Web UI動畫年表
4. 定時檢查動畫更新
```

---

## 2023/01/02
```
---Log---
1. 修正Myself method中finish_list的部分應為year_list。
2. 新增Myself method - finish_list。
3. 更新Myself的單元測試。
4. Web UI主頁完成。
5. API查詢貯列功能完成
6. 貯列管理器功能完成。
```
### 2023/01/02 Dev's Diary
今天(1/1)睡到早上11點才起床，好久沒睡到這麼晚了。

---

## 2023/01/01
```
---Log---
1. M3U8下載器錯誤重試功能完成。
2. 新增移除暫存資料夾中空資料夾的功能。
3. 改變檢查資料夾是否存在的時機。
4. M3U8下載器暫停功能完成。
5. 新增貯列管理器。
```

---

## 2022/12/28
```
---Log---
1. async_io/async_requests中new_session的Timeout修改為conn_timeout
2. 補上modules/m3u8.py的註解。
3. myself.py單元測試完成。
4. 修正資料抓取效率。
5. 修正Websocket傳送的資料。
6. M3U8下載器完成。

# 核心功能重構得差不多了。

```

---

## 2022/12/25
```
---Log---
1. myself.py重構完成。
2. 將Myself method更改為非同步(async)。
3. 新增MyselfAnime類別，用以儲存每一個影片的資料(tid, vid, m3u8_url)。
4. 新增MyselfAnimeTable類別，用以儲存動畫資料(網址, 名稱, 資料...)。
5. 導入自製通用模組modules.json。
6. 導入自製通用模組modules.threading_。
7. 導入自製通用模組configs.logging_config。
8. 導入自製通用模組configs.config。
9. config.py設定內容修改完成。
10.新增async_io.async_requests.py，用以發送非同步請求。
11.新增READMD.md
12.新增UpdateLog.md
13.將debug.html加到.gitignore

---TODO Detail---
1. 單元測試
2. m3u8下載器
```
