# MyselfAnimeDownloader_WebUI
Myself下載器，使用Web UI。下載方式部份參考至 https://github.com/hgalytoby/MyselfAnimeDownloader

此程式依賴於[Myself](https://myself-bbs.com/)，需網站存在才可使用。

## 當前版本
Release 1.0

## 運行依賴
1.此專案依賴於`FFmpeg`，請確保在電腦環境中有`FFmpeg`。

檢查方式:
 - 1.開啟命令提示字元 (`Win+R`輸入`cmd`後按確定)。
 - 2.再命令提示字元中輸入`ffmpeg -version`。
 - 3.輸入後請確保畫面中有出現類似以下內容之畫面。
   ![Imgur](https://i.imgur.com/Pc3L0nl.png)
 - 4.如果出現`ffmpeg' 不是內部或外部命令、可執行的程式或批次檔。`，請依照[說明](#附錄-安裝ffmpeg)安裝`FFmpeg`。

## 運行說明 - 透過EXE
1.前往[Release](https://github.com/AloneAlongLife/MyselfAnimeDownloader_WebUI/releases/latest)頁面。

2.選擇`MyselfAnimeDownloader WebUI.exe`並下載。

3.下載完成後啟動程式，Windwos會跳出警示~~因為我沒買憑證~~，請按`其他資訊 > 仍要執行`。

4.完成。

※注意事項:為了降低網路流量，在運行時會產生快取檔案，因此建議創建一個資料夾，並將程式放置於其中運行。

## 運行說明 - 透過Python
1.建議使用`Python 3.10`以上的版本<br>
雖然我的開發環境是在`Python 3.10.4`，但大部分的語法應該都可以兼容於`Python 3.6`以後的版本，所以基本上`Python 3.6`以後的版本都可以運行。

2.從Github獲取更新(可選，但不建議，因為平常會在兩個地方工作，所以)<br>

3.創建虛擬環境(可選)<br>
使用`python3 -m venv .venv`創建一個位於`.venv`的虛擬環境。

4.安裝依賴套件<br>
使用`pip3 -r .\requirements.txt`安裝依賴套件。

5.運行程式<br>
使用`python3 main.py`運行程式。

## 開發日誌(2023/01/12)
[查看開發日誌](UpdateLog.md/#20230112)

## 開發環境
```
 - Windows:
    - 版本: Windows 10 Pro 21H1
    - OS組建: 19043.2130
 
 - Environment
    - Python: 3.10.4
    - pip: 22.0.4
    - FFmpeg: 2022-04-28-git-ec07b15477-full_build
 
 - Browser
    - Opera GX
       - 版本: LVL 4 (core: 93.0.4585.78)
       - Chromium 版本: 107.0.5304.110
    - Microsoft Edge
       - 版本: 108.0.1462.54
       - Chromium 版本: 108.0.0.0

 - IDE
    - Visual Studio Code     v1.74.1
    - Extensions
       - Pylance             v2022.3.1
       - Python              v2022.20.1
       - HTML CSS Support    v1.13.1
       - Markdown All in One v3.5.0
```

## 附錄-安裝FFmpeg
1.前往FFmpeg[官方網站](https://ffmpeg.org)，並點擊`Download`按鈕。
![Imgur](https://i.imgur.com/GVuZl37.png)

2.將游標移至左下角`Windows`圖示上，並點擊下方第一個連結`Windows builds from gyan.dev`。
![Imgur](https://i.imgur.com/foZ8ssO.png)

3.在網頁中間點擊`ffmpeg-git-full.7z`進行下載。
![Imgur](https://i.imgur.com/9r8VEYZ.png)

4.下載完成後將其解壓縮並放置到任意處，在這裡以`C:\`作為示範。
![Imgur](https://i.imgur.com/dz7GdMH.png)

5.進入資料夾內尋找`bin`資料夾，將資料夾的路徑複製下來。
 - 注意:是`bin`資料夾的路徑，複製下來的路徑應類似於`C:\ffmpeg-2022-12-21-git-eef763c705-full_build\bin`，結尾是`bin`。
![Imgur](https://i.imgur.com/rATcMev.png)

6.開啟設定，點擊`系統 > 關於`。
![Imgur](https://i.imgur.com/IzvclQP.png)

7.尋找`相關設定 > 進階系統設定`，開啟`系統內容`視窗。
![Imgur](https://i.imgur.com/aftwiuW.png)

8.點擊`環境變數(N)...`，並在上方`xxx 的使用者變數(U)`方塊內找到`Path`。
![Imgur](https://i.imgur.com/fj8qMbM.png)

9.點擊`編輯`開啟編輯視窗，並按右方`新增(N)`，隨後將剛剛複製的路徑貼上。
![Imgur](https://i.imgur.com/ECCXkuV.png)

10.點擊確定關閉所有視窗後，再次開啟命令提示字元並輸入`ffmpeg -version`檢查，若出現類似於以下畫面之內容就是成功了。
![Imgur](https://i.imgur.com/Pc3L0nl.png)
