console.log("Hello world!");

const selectionWords = ["hello", "world", "gup", "gulp", "guh", "1", "2", "3", "4", "5", "6", "7", "8"];
const poemWords = [];

const poemSelector = document.getElementById("poem-selector");
const poemContainer = document.getElementById("poem-container");
const wordCounter = document.getElementById("word-counter");
const submitButton = document.getElementById("submit-button");

function addWord(word) {
    if (poemWords.length < 10) {
        poemWords.push(word);
    } else {
        console.error("Cannot add word: either empty or poem already has 10 words.");
    }
    redrawPoem();
}

function removeWord(index) {
    console.info(`Removing word at index: ${index}`);
    if (index >= 0 && index < poemWords.length) {
        poemWords.splice(index, 1);
    } else {
        console.error("Cannot remove word: index out of bounds.");
    }
    redrawPoem();
}

function redrawPoem() {
    poemSelector.innerHTML = "";
    selectionWords.forEach((word, index) => {
        const wordElement = document.createElement("span");
        wordElement.textContent = word;
        wordElement.classList.add("word")
        if (poemWords.includes(index) || poemWords.length >= 10) {
            wordElement.classList.add("selected");
        } else {
            wordElement.addEventListener("click", () => {
                addWord(index);
            });
        }
        poemSelector.appendChild(wordElement);
    });
    poemContainer.innerHTML = "";
    poemWords.forEach((word, index) => {
        const wordElement = document.createElement("span");
        wordElement.textContent = selectionWords[word];
        wordElement.classList.add("word")
        wordElement.addEventListener("click", () => {
            removeWord(index);
        });
        poemContainer.appendChild(wordElement);
    });
    wordCounter.innerHTML = `${poemWords.length}/10 words`;
    if (poemWords.length >= 1){
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
}

function submitPoem(player) {
    let poem = "";
    poemWords.forEach((wordIndex) => {
        poem += selectionWords[wordIndex] + " ";
    });
    poem = poem.trim();

//     Send the poem to the server
    fetch("/api/submit-poem", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            player_id: player,
            poem: poem
        })
    }).then(response => response.json())
      .then(data => {
          console.log(data);
      });
    window.location.href = "/game";
}

redrawPoem();