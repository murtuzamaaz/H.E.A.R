function triggerSOS() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(position => {
        fetch('http://localhost:8000/api/send-sos', { // Update URL if deployed
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            timestamp: new Date().toISOString()
          })
        })
        .then(response => response.json())
        .then(data => alert(data.message || "SOS sent!"))
        .catch(error => alert("Error sending SOS: " + error));
      }, error => {
        alert("Unable to access location. Please enable GPS.");
      });
    } else {
      alert("Geolocation is not supported by your browser.");
    }
  }
// hello
