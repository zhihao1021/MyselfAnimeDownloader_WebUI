// 取得設定檔
function get_setting() {
    $.getJSON("/api/get-setting", "", (data)=>{
        document.querySelectorAll("#setting .setting-box .row input").forEach((ele)=>{
            let key = ele.name;
            ele.value = data[key];
        })
    })
}

// 傳送設定檔
function send_setting() {
    let data = {};
    document.querySelectorAll("#setting .setting-box .row input").forEach((ele)=>{
        let key = ele.name;
        data[key] = ele.value;
    })
    $.post("/api/send-setting", data)
}
