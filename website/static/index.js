function deleteEvent(eventId) {
  fetch("/delete-event", {
    method: "POST",
    body: JSON.stringify({ eventId: eventId }),
  }).then((_res) => {
    window.location.href = "/my-events";
  });
}

function sendEvent(eventId) {
  fetch("/send-event", {
    method: "POST",
    body: JSON.stringify({ eventId: eventId }),
  }).then((_res) => {
    window.location.href = "/view-event";
  });
}