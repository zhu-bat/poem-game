const getJSON = async url => {
  const response = await fetch(url);
  if(!response.ok) // check if response worked (no 404 errors etc...)
    throw new Error(response.statusText);

  const data = response.json(); // get JSON from the response
  return data; // returns a promise, which resolves to this data value
}

let selectionWords = [];
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

function clearPoem() {
     while (poemWords.length > 0) {
        removeWord(0)
    }
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
          // Sleep 1000ms
            setTimeout(() => {
                window.location.reload();
            }, 1000);
      });
}

getJSON("/api/words").then(data => {
    selectionWords = Object.values(data["words"]);
    selectionWords = selectionWords.sort((a, b) => a.localeCompare(b));
    selectionWords = selectionWords.sort((a, b) => b.length - a.length);
    console.log(data);
    redrawPoem();
}).catch(error => {
    console.error(error);
});