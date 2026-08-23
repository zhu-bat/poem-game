const timeout1 = setTimeout(change1, 1000);
const timeout2 = setTimeout(change2, 2000);

function change1() {
    document.getElementById("start").style.display = "block";
}



function change2() {
    document.querySelector(".header").style.display = "none";
    document.querySelector(".workspace").style.display = "block";
}

