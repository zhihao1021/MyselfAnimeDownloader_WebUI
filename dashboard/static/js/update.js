let week_update_day = -1;

function show_update(page) {
    document.querySelector("#update-all").style.display = "none";
    document.querySelector("#update-year").style.display = "none";
    document.querySelector("#update-week").style.display = "none";
    switch (page) {
        case 0:
            document.querySelector("#update-all").style.display = "";
            break;
        case 1:
            document.querySelector("#update-year").style.display = "";
            break
        case 2:
            document.querySelector("#update-week").style.display = "";
            break;
    }
}

function get_week_anime() {
    $.getJSON("/api/get-week-anime", "", (data)=>{
        let week_ele = document.querySelectorAll("#update .week-day");
        let week_day = new Date().getDay();
        week_update_day = week_day;
        week_day--;
        if (week_day == -1) {week_day = 6}
        week_ele.forEach((ele, index)=>{
            if (index == week_day) {
                ele.classList.add("act");
            }
            else {
                ele.classList.remove("act");
            }
        })

        data.forEach((day_data, index)=>{
            let total = day_data.length;
            if (total == 0) {
                week_ele.querySelector(".no-ani").style.display = "";
                return
            }
            day_data.forEach((anime_tuple, ani_index)=>{
                let anime = anime_tuple[0];
                let update_text = anime_tuple[1];

                let ele = document.createElement("div");
                ele.classList.add("ani-block");
                ele.url = anime.URL;
                ele.onclick = function () {
                    search(this.url);
                    _last_page = 4;
                }

                let title = document.createElement("p");
                title.classList.add("title")
                title.textContent = anime.NAME;

                let update = document.createElement("p");
                update.classList.add("update");
                update.textContent = update_text;

                ele.appendChild(title);
                ele.appendChild(update);

                week_ele[index].appendChild(ele);

                if (ani_index < total - 1) {
                    let hr = document.createElement("hr");
                    hr.classList.add("hor-hr");
                    week_ele[index].appendChild(hr);
                }
            })
        });
    })
}
