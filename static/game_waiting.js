const getJSON = async url => {
  const response = await fetch(url);
  if(!response.ok)
    throw new Error(response.statusText);

  return response.json();
}

const playerListContainer = document.getElementById('player-list');

function waitForPhase(phase) {
  const intervalId = setInterval(() => {
    console.log(`Waiting for phase ${phase}`);
    getJSON("/api/server")
      .then(data => {
        console.log(data);
        if (data['phase'] === phase) {
          clearInterval(intervalId);
          window.location.reload();
        }
        if (phase === 'voting' && data['all_poems_submitted']) {
          clearInterval(intervalId);
          window.location.reload();
        }
        if (phase === 'results' && data['all_votes_submitted']) {
          clearInterval(intervalId);
          window.location.reload();
        }

        let subType = phase === 'voting' ? 'poem_submitted' : 'vote_submitted';
        drawPlayerList(Object.values(data['players']), subType);
      })
      .catch(error => {
        console.error(error);
      });
  }, 3000);
}


function drawPlayerList(players, sub_type) {
    playerListContainer.innerHTML = '';
    players.forEach(player => {
        const playerDiv = document.createElement('div');
        const statusSpan = document.createElement('span');
        statusSpan.textContent = player[sub_type] ? '✔' : '✘';
        statusSpan.style.display = 'inline-block';
        statusSpan.style.width = '2em';
        const nameSpan = document.createElement('span');
        nameSpan.textContent = player['name'];
        playerDiv.appendChild(statusSpan);
        playerDiv.appendChild(nameSpan);
        playerListContainer.appendChild(playerDiv);
    });
}

function drawVipPlayerList(players) {
    playerListContainer.innerHTML = '';
    players.forEach(player => {
        const playerDiv = document.createElement('div');
        const vipSpan = document.createElement('span');
        vipSpan.textContent = player['vip'] ? '*' : '';
        vipSpan.style.display = 'inline-block';
        vipSpan.style.width = '2em';
        const nameSpan = document.createElement('span');
        nameSpan.textContent = player['name'];
        playerDiv.appendChild(vipSpan);
        playerDiv.appendChild(nameSpan);
        playerListContainer.appendChild(playerDiv);
    });
}