function onload() {
    hash_change();
    set_color();
}

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

function set_color() {
    let color = Cookies.get("color_mode");
    console.log(color);
    let root = document.querySelector(':root');
    if (color == "1") {
        root.style.setProperty("--background-color",  "255, 255, 255");
        root.style.setProperty("--secondground-color",  "230, 230, 230");
        root.style.setProperty("--contrast-color",  "0, 0, 0");
        root.style.setProperty("--sec-contrast-color",  "255, 130, 0");
        root.style.setProperty("--primary-color",  "150, 150, 150");
        root.style.setProperty("--second-color",  "60, 60, 60");
    }
    else {
        root.style.setProperty("--background-color",  "33, 33, 33");
        root.style.setProperty("--secondground-color",  "50, 50, 50");
        root.style.setProperty("--contrast-color",  "230, 230, 230");
        root.style.setProperty("--sec-contrast-color",  "255, 130, 0");
        root.style.setProperty("--primary-color",  "90, 90, 90");
        root.style.setProperty("--second-color",  "144, 144, 144");
    }
}
