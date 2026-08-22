const getJSON = async url => {
  const response = await fetch(url);
  if(!response.ok) // check if response worked (no 404 errors etc...)
    throw new Error(response.statusText);

  const data = response.json(); // get JSON from the response
  return data; // returns a promise, which resolves to this data value
}

function waitForPhase(phase) {
  const intervalId = setInterval(() => {
    console.log(`Waiting for phase ${phase}`);
    getJSON("/api/server")
      .then(data => {
        console.log(data);
        if (data['phase'] === phase) {
          clearInterval(intervalId);
          window.location.href = "/game";
        }
      })
      .catch(error => {
        console.error(error);
      });
  }, 3000);
}
