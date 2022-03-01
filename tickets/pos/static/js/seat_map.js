const roomName = JSON.parse(document.getElementById('js-data').textContent).event_id;

console.log(roomName)

const chatSocket = new WebSocket(
    'wss://'
    + window.location.host
    + '/ws/seat_selection/'
    + roomName
    + '/'
);

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const seat = document.querySelector('#'+data.seat_code)
    switch (data.action) {
        case "select":
            seat.src = seat.src.replace("none", "selected");
            break;
        case "block":
            seat.src = seat.src.replace("none", "booked");
            break;
        case "unblock":
            seat.src = seat.src.replace("selected", "none");
            seat.src = seat.src.replace("booked", "none");
            break;
    
        default:
            break;
    }
    //document.querySelector('#chat-log').value += (data.message + '\n');
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};

function seatClick(event){
    console.log("Click detectado")
    let x = event.target;
    if (x.tagName == "IMG") {
        let seat_code = x.id;
        let actual_status = "";
        if (x.src.includes("none")){
            actual_status = "Free"
        }
        if (x.src.includes("selected")){
            actual_status = "Yours"
        }
        if (x.src.includes("booked")){
            actual_status = "Blocked"
        }
        switch (actual_status) {
            case "Free":
                chatSocket.send(JSON.stringify({
                    'seat_code' : x.id,
                    'action': 'select'
                }));
                break;

            case "Yours":
                chatSocket.send(JSON.stringify({
                    'seat_code' : x.id,
                    'action': 'unselect'
                }));
        
            default:
                break;
        }
    }
}
