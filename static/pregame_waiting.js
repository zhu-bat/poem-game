const getJSON = async url => {
  const response = await fetch(url);
  if(!response.ok)
    throw new Error(response.statusText);

  return response.json();
}

const playerListContainer = document.getElementById('player-list');
const startGameElement = document.getElementById('start-game');
const startHintElement = document.getElementById('start-hint');
const dotsElement = document.getElementById('dots');

function waitForPhase(phase, player) {
  const intervalId = setInterval(() => {
    console.log(`Waiting for phase ${phase}`);
    getJSON("/api/server")
      .then(data => {
        if (data['phase'] === phase) {
          clearInterval(intervalId);
          window.location.reload();
        }

        let playerData = data['players'][player];
        if (playerData === undefined) {
            window.location.reload();
        }

        let isVip = playerData['vip'];
        let playerCount = Object.values(data['players']).length;

        drawPlayerList(Object.values(data['players']), isVip);

        if (playerCount < 3) {
            startGameElement.style.display = 'none';
            startHintElement.textContent = "Game can only start when there are 3 or more players.";
        } else if (!isVip) {
            startGameElement.style.display = 'none';
            startHintElement.textContent = "Waiting for VIP to start game...";
        } else {
            startGameElement.style.display = 'block';
            startHintElement.textContent = "Press Start game when everyone is ready!";
        }


      })
      .catch(error => {
        console.error(error);
      });
  }, 3000);
}

function drawPlayerList(players, isVip) {
    playerListContainer.innerHTML = '';
    players.forEach(player => {
        const playerDiv = document.createElement('div');
        const vipSpan = document.createElement('span');
        vipSpan.textContent = player['vip'] ? '*' : '';
        vipSpan.style.display = 'inline-block';
        vipSpan.style.width = '2em';
        vipSpan.style.color = '#88c9f9';
        const nameSpan = document.createElement('span');
        nameSpan.textContent = player['name'];
        playerDiv.appendChild(vipSpan);
        playerDiv.appendChild(nameSpan);
        if (isVip && !player['vip']) {
            playerDiv.onclick = () => kickPlayer(player['id']);
            playerDiv.title = 'Click to kick this player';
            playerDiv.classList.add('kickable-player');
        }
        playerListContainer.appendChild(playerDiv);
    });
}

function kickPlayer(player) {
    fetch("/api/kick-player", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            player_id: player
        })
    }).then(response => response.json());
}

setInterval(() => {
    const newLen = (dotsElement.textContent.length % 3) + 1;
    let newDots = ""
    for (let i = 0; i < newLen; i++) {
        newDots += "."
    }
    dotsElement.textContent = newDots;
}, 500);
