const getJSON = async url => {
  const response = await fetch(url);
  if(!response.ok)
    throw new Error(response.statusText);

  return response.json();
}

const playerListContainer = document.getElementById('player-list');
const startGameElement = document.getElementById('start-game');
const startHintElement = document.getElementById('start-hint');

function waitForPhase(phase, player) {
  const intervalId = setInterval(() => {
    console.log(`Waiting for phase ${phase}`);
    getJSON("/api/server")
      .then(data => {
        if (data['phase'] === phase) {
          clearInterval(intervalId);
          window.location.reload();
        }
        drawPlayerList(Object.values(data['players']));

        let isVip = data['players'][player]['vip'];
        let playerCount = Object.values(data['players']).length;

        if (playerCount < 3) {
            startGameElement.style.display = 'none';
            startHintElement.textContent = "Waiting for more players to join...";
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

function drawPlayerList(players) {
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
        playerListContainer.appendChild(playerDiv);
    });
}