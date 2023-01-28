const color_style = [
    "background-color",
    "secondground-color",
    "contrast-color",
    "sec-contrast-color",
    "second-color"
]
let last_keyword = "";

function onload() {
    hash_change();
    set_color();
}

function postJSON (url, data, callback=null) {
    if (typeof data === "object") {
        data = JSON.stringify(data);
    }
    $.ajax({
        url: url,
        type: "POST",
        contentType:"application/json; charset=utf-8",
        dataType: "json",
        data: data,
        success: callback
    });
};

// 切換頁面
function hash_change() {
    let hash = location.hash.slice(1), finded=false;
    document.querySelectorAll(".page").forEach((element)=>{
        if (element.id == hash) {
            element.style.display="";
            finded = true;
        }
        else {
            element.style.display="none";
        }
    })
    if (finded) {return;}
    document.querySelector("#home").style.display="";
    location.hash = "home"
}

// 切換主題
function switch_color() {
    let color = Cookies.get("color_mode");
    if (color == "1") {
        Cookies.set("color_mode", "0");
        document.querySelector("#switch-color").textContent = "light_mode";
    }
    else {
        Cookies.set("color_mode", "1");
        document.querySelector("#switch-color").textContent = "dark_mode";
    }
    set_color();
}
function switch_custom(ele=null) {
    let color = Cookies.get("custom_color");
    if (color == "1") {
        Cookies.set("custom_color", "0");
        if (ele != null) {
            ele.textContent = "開啟自訂色彩";
        }
    }
    else {
        Cookies.set("custom_color", "1");
        set_custom();
        if (ele != null) {
            ele.textContent = "關閉自訂色彩";
        }
    }
    set_color();
}

// 設置主題
function set_color() {
    let root = document.querySelector(':root');
    if (Cookies.get("custom_color") == "1") {
        let colors = Cookies.get("colors");
        if (colors == undefined) {return}
        colors = colors.split(";");
        color_style.forEach((value, index)=>{
            root.style.setProperty(`--${value}`, colors[index]);
        })
        return;
    }
    let color = Cookies.get("color_mode");
    if (color == "0") {
        root.style.setProperty("--background-color", "33, 33, 33");
        root.style.setProperty("--secondground-color", "50, 50, 50");
        root.style.setProperty("--contrast-color", "255, 255, 255");
        root.style.setProperty("--sec-contrast-color", "255, 130, 0");
        root.style.setProperty("--second-color", "90, 90, 90");
    }
    else if (color == "1") {
        root.style.setProperty("--background-color", "255, 255, 255");
        root.style.setProperty("--secondground-color", "230, 230, 230");
        root.style.setProperty("--contrast-color", "0, 0, 0");
        root.style.setProperty("--sec-contrast-color", "100, 161, 222");
        root.style.setProperty("--second-color", "150, 150, 150");
    }
}
function init_custom() {
    let colors = Cookies.get("colors");
    let root = document.querySelector(':root');
    if (colors == undefined) {colors = ""}
    colors = colors.split(";");

    let new_colors = [];
    color_style.forEach((value, index)=>{
        let _color = colors[index];
        if (_color == undefined) {_color = ""}
        if (_color.split(",").length < 3) {
            new_colors.push(
                root.style.getPropertyValue(`--${value}`)
            );
        }
        else {
            new_colors.push(_color);
        }
    })
    Cookies.set("colors", new_colors.join(";"));
}
function read_custom() {
    init_custom();
    let setting_box = document.querySelector("#about .setting-box");
    
    let colors = Cookies.get("colors").split(";");

    setting_box.querySelectorAll("div.row").forEach((ele, index)=>{
        let color = colors[index].split(",");

        ele.querySelectorAll("input").forEach((inp_ele, ind)=>{
            inp_ele.value = parseInt(color[ind]);
        })
    });
}
function set_custom() {
    init_custom();
    let colors = [];
    document.querySelectorAll("#about .setting-box div.row").forEach((ele)=>{
        let value = [];
        ele.querySelectorAll("input").forEach((inp_ele)=>{
            let _val = inp_ele.value;
            if (_val == "") {_val = 0;}
            value.push(_val);
        })
        colors.push(value.join(", "));
    });
    Cookies.set("colors", colors.join(";"));

    set_color();
    read_custom();
}
function restore_custom() {
    let origin_mode = Cookies.get("custom_color");
    Cookies.remove("colors");
    if (origin_mode == "0") {
        read_custom();
        return;
    }
    switch_custom();
    read_custom();
    switch_custom();
}

// 搜尋
function search(keyword, from_cache=true) {
    last_keyword = keyword;
    postJSON("/api/search", {"keyword": keyword, "from-cache": from_cache}, (result)=>{
        if (result.type == "anime") {
            // 回傳動畫
            update_anime(result.data);
        }
        else if (result.type == "search") {
            update_results(result.data);
        }
        else {
            show_page(3);
        }
    })
    show_page(0);
    location.hash = "info";
}

// 以下為彩虹色

const hsl2rgb_tex = (h,s,l) => {
    h %= 360;
   let a = s * Math.min(l,1-l);
   let f = (n,k=(n+h/30)%12) => l - a*Math.max(Math.min(k-3,9-k,1),-1);
   return `${f(0)*255}, ${f(8)*255}, ${f(4)*255}`;
}

function b_1(h=0) {
    h++;
    h %= 360;
    let res = "";
    for (let i = 0; i < 40; i++) {
        res += `hsl(${(h + 9 * i) % 360}, 100%, 50%, 0.8), `;
    }
    res += `hsl(${h}, 100%, 50%, 0.8)`;
    let root = document.querySelector(':root');
    root.style.setProperty("--b",  res);
    document.querySelector("#switch-q").remove();
    setTimeout(b_2, 100);
}

function b_2(h=0) {
    let root = document.querySelector(':root');
    h %= 360;
    root.style.setProperty("--background-color",  hsl2rgb_tex(h, 1, 0.5));
    root.style.setProperty("--secondground-color",  hsl2rgb_tex(h + 270, 1, 0.5));
    root.style.setProperty("--contrast-color",  hsl2rgb_tex(h + 180, 1, 0.5));
    root.style.setProperty("--sec-contrast-color",  hsl2rgb_tex(h + 135, 1, 0.5));
    root.style.setProperty("--second-color",  hsl2rgb_tex(h + 90, 1, 0.5));
    setTimeout(b_2, 100, h+20);
}
