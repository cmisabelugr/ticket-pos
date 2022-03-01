
const videoElem = document.getElementById("scanner-area");
var activeSeatCode = "";
const qrScanner = new QrScanner(videoElem, result => processResult(result));
var regTickets = /\/t\/(\w{3,6})/g;
const apiURL = JSON.parse(document.getElementById('js-data').textContent).api_url;
const csrfToken = JSON.parse(document.getElementById('js-data').textContent).csrf;



function showScanner(seat_code){
    $('#scanModal').modal('show');
    qrScanner.start();
    activeSeatCode = seat_code;
    console.log("Escaneando asiento ", seat_code);
}

function processResult(result){
    console.log(result);
    //console.log(regTickets.exec(result))
    reg  = regTickets.exec(result);
    if (!reg){
        reg  = regTickets.exec(result);
    }
    console.log(reg);
    r = reg[1];
    console.log("Asignando al asiento ", activeSeatCode, " el ticket ", r);
    $('#scanModal').modal('hide');
    qrScanner.stop();
    let data = new FormData();
    data.append("action", 'book');
    data.append("ticket_code", r);
    data.append("seat_code", activeSeatCode);
    data.append("csrfmiddlewaretoken", csrfToken);
    axios.post(apiURL,data)
    .then(function (response) {
        console.log(response)
        res = response.data
        if (res.status=="ok"){
            document.getElementById(activeSeatCode).innerHTML = "Asiento "+ activeSeatCode + 
            "<span class='badge badge-secondary badge-pill' onClick='freeTicket("+'"'+activeSeatCode+'","'+res.ticket_serial+'"' +")'>Ticket "+res.ticket_serial+" - Liberar</span>"
        }
        else{
            if(res.status =="error" && res.reason =="usedTicket"){
                $('#errorModal').modal('show');
            }
            console.log(res)
        }
    })
    .catch(error => console.log(error))
}

function freeTicket(seat_code, ticket_id){
    let data = new FormData();
    data.append("action", 'free');
    data.append("ticket_code", ticket_id);
    data.append("csrfmiddlewaretoken", csrfToken);
    axios.post(apiURL,data)
    .then(function (response) {
        console.log(response)
        res = response.data
        if (res.status=="ok"){
            document.getElementById(seat_code).innerHTML = "Asiento "+ seat_code + 
            "<span class='badge badge-primary badge-pill' onClick='showScanner("+'"'+seat_code+'"'+")'>Asignar ticket</span>"
        }
        else{
            console.log(res)
        }
    })
    .catch(error => console.log(error))
}
