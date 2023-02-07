## 2023/01/27
Release 1.2

1. 修正requests函式例外處理Logger位置。
2. 關閉SSL驗證，避免部分電腦發生憑證錯誤。
3. 棄用websockets套件，改為aiohttp附帶之WebSocket。