
const videoElem = document.getElementById("scanner-area");
var activeSeatCode = "";
const qrScanner = new QrScanner(videoElem, result => processResult(result));
var regTickets = /\/t\/(\w{3,6})$/gm;
function showScanner(seat_code){
    $('#scanModal').modal('show');
    qrScanner.start();
    activeSeatCode = seat_code;
    console.log("Escaneando asiento ", seat_code);
}

function processResult(result){
    r = regTickets.exec(result)[1];
    console.log("Asignando al asiento ", activeSeatCode, " el ticket ", r);
    $('#scanModal').modal('hide');
    qrScanner.stop();
}