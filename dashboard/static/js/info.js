let _last_episode;

// 顯示分頁
function show_page(page) {
    document.querySelector("#info-loading").style.display = "none";
    document.querySelector("#info-results").style.display = "none";
    document.querySelector("#info-anime").style.display = "none";
    document.querySelector("#info-search").style.display = "none";
    switch (page) {
        case 0:
            document.querySelector("#info-loading").style.display = "";
            break;
        case 1:
            document.querySelector("#info-results").style.display = "";
            break
        case 2:
            document.querySelector("#info-anime").style.display = "";
            break;
        case 3:
            document.querySelector("#info-search").style.display = "";
    }
}

// 更新搜尋頁面
function update_results(data) {
    if (data.length == 0) {
        show_page(3);
        return;
    }
    data.forEach((value)=>{
        let ele = document.createElement("div");
        ele.classList.add("result-box");
        ele.url = value.URL;
        ele.onclick = function () {search(this.url);};
        let p_ele = document.createElement("p");
        p_ele.textContent = value.NAME;
        ele.appendChild(p_ele);
        document.querySelector("#info-results").appendChild(ele);
    })
    show_page(1);
}

// 更新資料頁面
function update_anime(data) {
    document.querySelector("#anime-img").src = data.IMAGE_URL

    document.querySelector("#anime-name .a-content").textContent = data.NAME
    document.querySelector("#anime-type .a-content").textContent = data.ANI_TYPE
    document.querySelector("#anime-pre-date .a-content").textContent = data.PRE_DATE
    document.querySelector("#anime-eps-num .a-content").textContent = data.EPS_NUM
    document.querySelector("#anime-author .a-content").textContent = data.AUTHOR
    document.querySelector("#anime-official-web .a-content").textContent = data.OFFICIAL_WEB
    document.querySelector("#anime-official-web .a-content").href =  data.OFFICIAL_WEB
    document.querySelector("#anime-remark .a-content").textContent = data.REMARKS
    document.querySelector("#anime-myself .a-content").textContent = data.URL
    document.querySelector("#anime-myself .a-content").href = data.URL
    
    document.querySelector("#anime-intro").textContent = data.INTRO

    let episodes = document.querySelector("#episodes");
    data.VIDEO_LIST.forEach((eps_data, index)=> {
        let new_ele = document.createElement("div");
        new_ele.classList.add("episode");
        new_ele.tid = eps_data.TID;
        new_ele.vid = eps_data.VID;
        new_ele.onclick = function (event) {selected(this, event);};
        new_ele.textContent = eps_data.EPS_NAME;
        new_ele.order = index;

        episodes.appendChild(new_ele);
    });
    _last_episode = 0;
    show_page(2);
}

// 當集數被選擇
function selected(ele, event=null) {
    if (event != null) {
        if (event.shiftKey) {
            let all_episode = document.querySelectorAll("#episodes .episode");
            let _s = Math.min(ele.order, _last_episode);
            let _e = Math.max(ele.order, _last_episode) + 1;
            _e = Math.min(_e, all_episode.length);

            document.querySelectorAll("#episodes .episode.sel").forEach((ele)=>{
                ele.classList.remove("sel");
            })
            for (let i = _s; i < _e; i++) {
                all_episode[i].classList.add("sel");
            }
            return;
        }
    }
    if (ele.classList.contains("sel")) {
        ele.classList.remove("sel");
        _last_episode = 0;
        return
    }
    ele.classList.add("sel");
    _last_episode = ele.order;
}

// 選擇特定集數
function select_episodes(inp) {
    inp = inp.replaceAll(" ", "");
    if (inp == "") {inp = "!-"}
    let select_list = inp.split(",");
    let all_episode = document.querySelectorAll("#episodes .episode");
    select_list.forEach((value)=>{
        value = value.trim();
        let remove = false;
        if (value.startsWith("!")) {
            remove = true;
            value = value.replace("!", "");
        }

        if (value.indexOf("-") != -1) {
            let value_list = value.split("-");
            let _v1 = parseInt(value_list[0]);
            let _v2 = parseInt(value_list[1]);
            if (isNaN(_v1)) {_v1 = 0;}
            if (isNaN(_v2)) {_v2 = all_episode.length;}
            let _s = Math.min(_v1, _v2) - 1;
            let _e = Math.max(_v1, _v2);
            _e = Math.min(_e, all_episode.length);
            for (let i = _s; i < _e; i++) {
                let ele = all_episode[i];
                if (ele == null) {continue;}
                if (remove) {
                    ele.classList.remove("sel");
                }
                else {
                    ele.classList.add("sel");
                }
            }
            return;
        }
        let i = parseInt(value);
        if (isNaN(i)) {return;}
        i = Math.max(0, Math.min(i, all_episode.length));
        i--;
        if (remove) {
            all_episode[i].classList.remove("sel");
        }
        else {
            all_episode[i].classList.add("sel");
        }
    })
}

// 發送選擇的集數
function send_episode() {
    let sel_episodes = document.querySelectorAll("#episodes .episode.sel");
    let data = {"ani_name": document.querySelector("#anime-name .a-content").textContent}
    let episodes = []
    sel_episodes.forEach((ele)=>{
        episodes.push({
            "eps_name": ele.textContent,
            "tid": ele.tid,
            "vid": ele.vid
        })
        ele.classList.remove("sel");
    })
    data["episodes"] = episodes;
    $.ajax("/api/download", {
        data: JSON.stringify(data),
        contentType: "application/json",
        type: "POST"
    })
}
