const _progress_bar_inner = '<div class="progress-text">\n\
    <div class="progress-title"></div>\n\
    <div class="progress-option ms act" onclick="_modify(this, event);">play_arrow</div>\n\
    <div class="progress-option ms act" onclick="_modify(this, event);">stop</div>\n\
    <div class="progress-option ms act" onclick="_modify(this, event);">keyboard_arrow_up</div>\n\
    <div class="progress-option ms act" onclick="_modify(this, event);">keyboard_arrow_down</div>\n\
</div>\n\
<div class="progress b_2" style="--proc: 0">0%</div>\n';

// 創造貯列元素
function gen_queue(id) {
    ele = document.createElement("div");
    ele.id = id;
    ele.classList.add("progress-bar");
    ele.innerHTML = _progress_bar_inner;
    return ele;
}

// 抓取資料
function fetch_queue() {
    let ws = new WebSocket(`ws://${location.host}/ws/download-queue`);
    ws.onmessage = (event)=>{
        callback(JSON.parse(event.data));
    }
    let callback = (json_data)=>{
        let keys = Object.keys(json_data);
        document.querySelectorAll("div.queue .progress-bar").forEach((element)=>{
            // 不在資料中的進度條
            if (keys.indexOf(element.id) == "-1") {
                // 移至最上方
                element.style.order = -1;
                // 停用按鈕
                element.querySelectorAll(".progress-option").forEach((_ele)=>{
                    _ele.classList.remove("act");
                })
            }
        });

        keys.forEach((value)=>{
            let target = document.querySelector(`#${value}`);
            let progress = json_data[value].progress;
            let status = json_data[value].status;
            let order = json_data[value].order;
            // 如果進度條不存在
            if (target == null) {
                if (status == 3 || status == 5 || status == 6) {
                    return;
                }
                _element = gen_queue(value);
                document.querySelector("div.queue").appendChild(_element);
                target = document.querySelector(`#${value}`);
            }

            let options = target.querySelectorAll(".progress-option");
            if (status == 0) {
                // 下載中
                options[0].textContent = "pause";
            }
            else if (status == 1) {
                // 暫停中
                options[0].textContent = "play_arrow";
            }
            
            if (status == 0 || status == 1) {
                options[0].classList.add("act")
                options[1].classList.add("act")
                options[2].classList.add("act")
                options[3].classList.add("act")
            }
            else if (status == 2 || status == 4) {
                options[0].classList.remove("act")
                options[1].classList.add("act")
                options[2].classList.add("act")
                options[3].classList.add("act")
            }
            else {
                options[0].classList.remove("act")
                options[1].classList.remove("act")
                options[2].classList.remove("act")
                options[3].classList.remove("act")
            }
            
            // 設置順序
            target.style.order = order;
            // 設置名稱
            target.querySelector(".progress-title").textContent = json_data[value].name;
            target.querySelector(".progress-title").title = json_data[value].name;
            // 設置進度
            target.querySelector(".progress").textContent = `${(progress * 100).toFixed(1)}%`;
            target.querySelector(".progress").style.setProperty("--proc", progress * 100);
        })
    };
}

function _modify(ele, event) {
    if (ele.classList.contains("act") == -1) {
        return;
    }
    id = ele.parentElement.parentElement.id;
    switch (ele.textContent) {
        case "pause":
            postJSON("/api/queue-modify", {"downloader-id": id, "modify": "pause"})
            ele.textContent = "play_arrow";
            break;
        case "play_arrow":
            postJSON("/api/queue-modify", {"downloader-id": id, "modify": "resume"})
            ele.textContent = "pause";
            break;
        case "stop":
            postJSON("/api/queue-modify", {"downloader-id": id, "modify": "stop"})
            break;
        case "keyboard_arrow_up":
            if (event.shiftKey) {
                postJSON("/api/queue-modify", {"downloader-id": id, "modify": "highest"});
            }
            else {
                postJSON("/api/queue-modify", {"downloader-id": id, "modify": "upper"});
            }
            break;
        case "keyboard_arrow_down":
            if (event.shiftKey) {
                postJSON("/api/queue-modify", {"downloader-id": id, "modify": "lowest"});
            }
            else {
                postJSON("/api/queue-modify", {"downloader-id": id, "modify": "lower"})
            }
            break;
    }
    ele.classList.remove("act");
    setTimeout(()=>{ele.classList.add("act");}, 1000);
}
