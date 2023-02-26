function get_broadcast() {
    let broadcast_ws = new WebSocket(`ws://${location.host}/ws/broadcast`);
    broadcast_ws.onmessage = (event)=>{
        let data = JSON.parse(event.data)

        let ele = document.createElement("div");
        ele.classList.add("message-box");

        let icon = document.createElement("div");
        icon.classList.add("ms");
        icon.classList.add(data.type);
        icon.innerText = data.type == "error" ? "report" : data.type;

        let content = document.createElement("div");
        content.innerText = data.message;

        let close = document.createElement("div");
        close.classList.add("ms");
        close.classList.add("close");
        close.onclick = function () {this.parentNode.remove();};
        close.innerText = "close";

        ele.appendChild(icon);
        ele.appendChild(content);
        ele.appendChild(close);


        document.querySelector("#message-bar").appendChild(ele);
        setTimeout(()=>{
            ele.classList.add("count-down");
            setTimeout(()=>{try{ele.remove()}catch{}}, 6100);
        }, 500);
    }
}

function close_tab(ele) {
    ele.parentNode.remove();
}