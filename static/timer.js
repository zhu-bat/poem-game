const timerElement = document.getElementById("timer");

function startTimer(endTime) {
    const intervalId = setInterval(() => {
        const currentTime = Math.floor(Date.now() / 1000);
        const timeRemaining = endTime - currentTime;
        console.log(`Time remaining: ${timeRemaining}s`);
        if (timeRemaining < 0) {
            clearInterval(intervalId);
            window.location.href = "/game";
        } else {
            timerElement.textContent = `${timeRemaining}s`;
        }
    }, 1000);
}
