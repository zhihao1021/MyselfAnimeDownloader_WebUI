function show_page(page) {
    document.querySelector("#info-loading").style.display = "none";
    document.querySelector("#info-results").style.display = "none";
    document.querySelector("#info-anime").style.display = "none";
    switch (page) {
        case 0:
            document.querySelector("#info-loading").style.display = "";
            break;
        case 1:
            document.querySelector("#info-results").style.display = "";
            break
        case 2:
            document.querySelector("#info-anime").style.display = "none";
            break;
    }
}