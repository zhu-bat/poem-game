
const timeout = setTimeout(updateScore, 2000);

function updateScore() {
    const scores = document.querySelectorAll('.score');

    for (const s of scores) {
        let [l, r] = s.innerHTML.split('+')
        s.innerHTML = Number(l) + Number(r)
    }
}
