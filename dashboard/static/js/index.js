function onload() {
    hash_change();
    set_color();
}

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

// 設置主題
function set_color() {
    let color = Cookies.get("color_mode");
    let root = document.querySelector(':root');
    if (color == "1") {
        root.style.setProperty("--background-color",  "255, 255, 255");
        root.style.setProperty("--secondground-color",  "230, 230, 230");
        root.style.setProperty("--contrast-color",  "0, 0, 0");
        root.style.setProperty("--sec-contrast-color",  "100, 161, 222");
        root.style.setProperty("--primary-color",  "150, 150, 150");
        root.style.setProperty("--second-color",  "60, 60, 60");
    }
    else {
        root.style.setProperty("--background-color",  "33, 33, 33");
        root.style.setProperty("--secondground-color",  "50, 50, 50");
        root.style.setProperty("--contrast-color",  "255, 255, 255");
        root.style.setProperty("--sec-contrast-color",  "255, 130, 0");
        root.style.setProperty("--primary-color",  "90, 90, 90");
        root.style.setProperty("--second-color",  "144, 144, 144");
    }
}

// 搜尋
function search(keyword) {
    $.post("/api/search", {"keyword": keyword}, (result)=>{
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
    root.style.setProperty("--primary-color",  hsl2rgb_tex(h + 90, 1, 0.5));
    root.style.setProperty("--second-color",  hsl2rgb_tex(h + 45, 1, 0.5));
    setTimeout(b_2, 100, h+20);
}
