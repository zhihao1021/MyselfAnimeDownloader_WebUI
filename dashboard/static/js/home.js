const _progress_bar_inner = '<div class="progress-text">\n\
    <div class="progress-title"></div>\n\
    <div class="progress-option ms">pause</div>\n\
    <div class="progress-option ms">stop</div>\n\
    <div class="progress-option ms">keyboard_arrow_up</div>\n\
    <div class="progress-option ms">keyboard_arrow_down</div>\n\
</div>\n\
<div class="progress" style="--proc: 0">0%</div>\n';

function gen_queue(id) {
    ele = document.createElement("div");
    ele.id = id;
    ele.classList.add("progress-bar");
    ele.innerHTML = _progress_bar_inner;
    return ele;
}

function fetch_queue(json_data) {
    let keys = Object.keys(json_data);

    document.querySelectorAll("div.queue .progress-bar").forEach((element)=>{
        if (keys.indexOf(element.id) == "-1") {
            element.style.order = -1;
            element.querySelectorAll(".progress-option").forEach((_ele)=>{
                _ele.classList.remove("act")
            })
        }
    })

    keys.forEach((value, index)=>{
        let target = document.querySelector(`#${value}`);
        let progress = json_data[value].progress;
        if (target == null) {
            _element = gen_queue(value);
            document.querySelector("div.queue").appendChild(_element);
            target = document.querySelector(`#${value}`);
        }
        
        target.style.order = index;
        target.querySelector(".progress-title").textContent = json_data[value].name;
        target.querySelectorAll(".progress-option").forEach((_ele)=>{
            _ele.classList.add("act")
        });
        target.querySelector(".progress").textContent = `${(progress * 100).toFixed(1)}%`;
        target.querySelector(".progress").style.setProperty("--proc", progress * 100);
    })
}
