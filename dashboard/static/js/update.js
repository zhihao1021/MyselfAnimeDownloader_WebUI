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
            ele.querySelectorAll(".ani-block").forEach((block)=>{
                ele.removeChild(block);
            });
            ele.querySelectorAll("hr").forEach((block)=>{
                ele.removeChild(block);
            });
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

function get_year_anime() {
    $.getJSON("/api/get-year-anime", "", (data)=>{
        let keys = Object.keys(data).reverse();
        let page = document.querySelector("#update-year");

        page.querySelectorAll(".season-block").forEach((ele)=>{
            page.removeChild(ele);
        })

        keys.forEach((key)=>{
            let anime_list = data[key];
            let season_block = document.createElement("div");
            season_block.classList.add("season-block");

            let season_title = document.createElement("div");
            season_title.classList.add("title");
            season_title.textContent = key;
            season_block.appendChild(season_title);

            let hr = document.createElement("hr");
            hr.classList.add("hor-hr");
            season_block.appendChild(hr);

            let animes = document.createElement("div");
            animes.classList.add("animes");

            anime_list.forEach((anime)=>{
                let ele = document.createElement("div");
                ele.classList.add("anime-block");

                let p = document.createElement("p");
                p.url = anime.URL;
                p.onclick = function () {
                    search(this.url);
                    _last_page = 4;
                }
                p.textContent = anime.NAME;
                p.title = anime.NAME;
                ele.appendChild(p);

                animes.appendChild(ele);
            })
            season_block.appendChild(animes);
            page.appendChild(season_block);
        });
    })
}
