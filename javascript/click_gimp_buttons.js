const socket = new WebSocket("ws://localhost:7861");

socket.addEventListener('open', e => {
    console.log('[gimporter] connection to the websockets server established');
});

socket.addEventListener('message', e => {
    elem_id = e.data;
    console.log(`[gimporter] received elem_id`, elem_id);
    gradioApp().querySelector(`#gimp_refresh_${elem_id}`).click();
});
