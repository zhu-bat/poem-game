const getJSON = async url => {
  const response = await fetch(url);
  if(!response.ok) // check if response worked (no 404 errors etc...)
    throw new Error(response.statusText);

  const data = response.json(); // get JSON from the response
  return data; // returns a promise, which resolves to this data value
}

let poems = {};
let selectedPoem = null;

const poemsContainer = document.getElementById("poems-container");
const submitButton = document.getElementById("submit-button");

function redrawPoems() {
    poemsContainer.innerHTML = "";
    // Iterate over key values
    Object.entries(poems['poems']).forEach(([index, poem]) => {
        console.log(`Redrawing poem at index ${index}: ${poem}`);
        const poemElement = document.createElement("div");
        poemElement.classList.add('poem-button');
        poemElement.textContent = poem;
        poemElement.classList.add("poem");
        if (selectedPoem === index) {
            poemElement.classList.add("selected");
        } else {
            poemElement.addEventListener("click", () => {
                selectedPoem = index;
                redrawPoems();
            });
        }
        poemsContainer.appendChild(poemElement);
    });
    if (selectedPoem !== null) {
        submitButton.disabled = false;
        submitButton.onclick = () => {
            submitVote(selectedPoem);
        };
    } else {
        submitButton.disabled = true;
    }
}

function submitVote(selected) {
    fetch("/api/submit-vote", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            poem_index: selected
        })
    }).then(response => response.json())
      .then(data => {
          console.log(data);
          // Sleep 1000ms
            setTimeout(() => {
                window.location.href = "/game";
            }, 1000);
      });
}

getJSON("/api/poems").then(data => {
    poems = data;
    const poemKeys = Object.keys(poems['poems']);
    if (poemKeys.length === 1) {
        submitVote(poemKeys[0]);
    } else if (poemKeys.length < 1) {
        submitVote(-1);
    }
    console.log(data);
    redrawPoems();
}).catch(error => {
    console.error(error);
});