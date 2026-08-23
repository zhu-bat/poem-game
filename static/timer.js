const timerElement = document.getElementById("timer");

function startTimer(endTime) {
    const intervalId = setInterval(() => {
        if (!endTime) {
            return;
        }
        const currentTime = Math.floor(Date.now() / 1000);
        const timeRemaining = endTime - currentTime;
        console.log(`Time remaining: ${timeRemaining}s`);
        if (timeRemaining < 0) {
            clearInterval(intervalId);
            window.location.reload()
        } else {
            timerElement.textContent = `${timeRemaining}s`;
        }
    }, 1000);
}
