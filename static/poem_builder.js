console.log("Hello world!");

const poemWords = [];

const poemContainer = document.getElementById("poem-container");

function addWord(word) {
    if (word && poemWords.length < 10) {
        poemWords.push(word);
    } else {
        console.error("Cannot add word: either empty or poem already has 10 words.");
    }
    redrawPoem();
}

function redrawPoem() {
    poemContainer.innerHTML = "";
    poemWords.forEach(word => {
        const wordElement = document.createElement("span");
        wordElement.textContent = word + " ";
        poemContainer.appendChild(wordElement);
    });
}