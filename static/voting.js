console.log("Hello world!");

const poems = ["Hello World!", "GUP!!!!!!", "This is a poem."];

let selectedPoem = null;

const poemsContainer = document.getElementById("poems-container");
const submitButton = document.getElementById("submit-button");

function redrawPoems() {
    poemsContainer.innerHTML = "";
    poems.forEach((poem, index) => {
        const poemElement = document.createElement("div");
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
    } else {
        submitButton.disabled = true;
    }
}

function submitVote(player) {
    fetch("/api/submit-vote", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            player_id: player,
            poem_index: selectedPoem
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

redrawPoems();