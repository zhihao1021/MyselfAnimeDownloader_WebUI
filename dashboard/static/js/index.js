function hash_change() {
    let hash = location.hash.slice(1), finded=false;
    document.querySelectorAll(".page").forEach((element)=>{
        if (element.id == hash) {
            element.style.display="block";
            finded = true;
        }
        else {
            element.style.display="none";
        }
    })
    if (finded) {return;}
    document.querySelector("#home").style.display="block";
    location.hash = "home"
}
