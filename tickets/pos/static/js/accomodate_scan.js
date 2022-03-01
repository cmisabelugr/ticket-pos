
const videoElem = document.getElementById("scanner-area");
const qrScanner = new QrScanner(videoElem, result => processResult(result));
var regTickets = /\/t\/(\w{3,6})/g;
const apiURL = JSON.parse(document.getElementById('js-data').textContent).api_url;
const csrfToken = JSON.parse(document.getElementById('js-data').textContent).csrf;
const event_id = JSON.parse(document.getElementById('js-data').textContent).event_id;

var ticket_list = [];

function beep() {
    var snd = new Audio("data:audio/wav;base64,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qJrx4KOQjahZxWbcZgztj2c49nKmkId44S71j0c8eV9yDK6uPRzx5X18eDvjvQ6yKo9ZSS6l//8elePK/Lf//IInrOF/FvDoADYAGBMGb7FtErm5MXMlmPAJQVgWta7Zx2go+8xJ0UiCb8LHHdftWyLJE0QIAIsI+UbXu67dZMjmgDGCGl1H+vpF4NSDckSIkk7Vd+sxEhBQMRU8j/12UIRhzSaUdQ+rQU5kGeFxm+hb1oh6pWWmv3uvmReDl0UnvtapVaIzo1jZbf/pD6ElLqSX+rUmOQNpJFa/r+sa4e/pBlAABoAAAAA3CUgShLdGIxsY7AUABPRrgCABdDuQ5GC7DqPQCgbbJUAoRSUj+NIEig0YfyWUho1VBBBA//uQZB4ABZx5zfMakeAAAAmwAAAAF5F3P0w9GtAAACfAAAAAwLhMDmAYWMgVEG1U0FIGCBgXBXAtfMH10000EEEEEECUBYln03TTTdNBDZopopYvrTTdNa325mImNg3TTPV9q3pmY0xoO6bv3r00y+IDGid/9aaaZTGMuj9mpu9Mpio1dXrr5HERTZSmqU36A3CumzN/9Robv/Xx4v9ijkSRSNLQhAWumap82WRSBUqXStV/YcS+XVLnSS+WLDroqArFkMEsAS+eWmrUzrO0oEmE40RlMZ5+ODIkAyKAGUwZ3mVKmcamcJnMW26MRPgUw6j+LkhyHGVGYjSUUKNpuJUQoOIAyDvEyG8S5yfK6dhZc0Tx1KI/gviKL6qvvFs1+bWtaz58uUNnryq6kt5RzOCkPWlVqVX2a/EEBUdU1KrXLf40GoiiFXK///qpoiDXrOgqDR38JB0bw7SoL+ZB9o1RCkQjQ2CBYZKd/+VJxZRRZlqSkKiws0WFxUyCwsKiMy7hUVFhIaCrNQsKkTIsLivwKKigsj8XYlwt/WKi2N4d//uQRCSAAjURNIHpMZBGYiaQPSYyAAABLAAAAAAAACWAAAAApUF/Mg+0aohSIRobBAsMlO//Kk4soosy1JSFRYWaLC4qZBYWFRGZdwqKiwkNBVmoWFSJkWFxX4FFRQWR+LsS4W/rFRb/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////VEFHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAU291bmRib3kuZGUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMjAwNGh0dHA6Ly93d3cuc291bmRib3kuZGUAAAAAAAAAACU=");  
    snd.play();
}

// Lo que podemos recibir es un:
//{
//    'status' : ['ok', 'invalidTicket', 'otherEvent', 'checkedIn', 'notPayed', 'blankTicket']
//}
function processResult(result){
    console.log(result);
    //console.log(regTickets.exec(result))
    reg  = regTickets.exec(result);
    if (!reg){
        reg  = regTickets.exec(result);
    }
    console.log(reg);
    try{
        r = reg[1];
    } catch(error){
        console.log("El escaner la ha liao");
    }
    beep();
    qrScanner.stop();
    let data = new FormData();
    data.append("action", 'verify');
    data.append("ticket_code", r);
    data.append("csrfmiddlewaretoken", csrfToken);
    axios.post(apiURL,data)
    .then(function (response) {
        console.log(response)
        res = response.data
        switch (res.status) {
            case "ok":
                alertElem = document.getElementById("mainAlert");
                alertElem.className = "alert alert-success"
                alertElem.textContent = "Ticket "+res.ticket_serial+"VALIDO. Asiento " + res.seat_code;
                t = {
                    serial : res.ticket_serial,
                    seat_code : res.seat_code,
                    qr_text : r
                }
                ticket_list.push(t);
                updateDisplay();
                break;

            case "invalidTicket":
                alertElem = document.getElementById("mainAlert");
                alertElem.className = "alert alert-danger"
                alertElem.textContent = "Ticket INVALIDO";
                
                break;

            case "otherEvent":
                alertElem = document.getElementById("mainAlert");
                alertElem.className = "alert alert-danger"
                alertElem.textContent = "Ticket para otro día";
                break;
            
            case "checkedIn":
                alertElem = document.getElementById("mainAlert");
                alertElem.className = "alert alert-info"
                alertElem.textContent = "Ticket duplicado. Ya está en sala";
                break;

            case "notPayed":
                alertElem = document.getElementById("mainAlert");
                alertElem.className = "alert alert-warning"
                alertElem.textContent = "Ticket no pagado. Desviar a taquilla";
                window.location.href = "/door/office_pay/"+event_id+"/"+r+"/";
                break;

            case "blankTicket":
                alertElem = document.getElementById("mainAlert");
                alertElem.className = "alert alert-danger"
                alertElem.textContent = "Ticket no activo";
                break;

            default:
                break;
        }
        
        setTimeout(startImageScan,500)
    })
    .catch(error => console.log(error))
}


on_scanner() // init function

function on_scanner() {
    let is_event = false; // for check just one event declaration
    let input = document.getElementById("scanner");
    input.addEventListener("focus", function () {
        if (!is_event) {
            is_event = true;
            input.addEventListener("keypress", function (e) {
                setTimeout(function () {
                    if (e.keyCode == 13) {
                        scanner(input.value); // use value as you need
                        input.select();
                    }
                }, 500)
            })
        }
    });
    document.addEventListener("keypress", function (e) {
        if (e.target.tagName !== "INPUT") {
            input.focus();
        }
    });
}

function scanner(value) {
    if (value == '') return;
    console.log(value)
    processResult(value);
}

function startImageScan(){
    qrScanner.start()
}

function updateDisplay(){
    const lista = document.getElementById("ticketList");
    lista.innerHTML= "";
    ticket_list.forEach((element) => {
        let l = document.createElement('li');
        l.className = "list-group-item";
        l.textContent = "Ticket " + element.serial+ " - Asiento " + element.seat_code;
        lista.append(l)
    })
}

function submitForm(){
    if (ticket_list){
        cadena = "";
        ticket_codes = []
        ticket_list.forEach(element => ticket_codes.push(element.qr_text))
        cadena = ticket_codes.join(',');
        formInput = document.getElementById("tickets_scanned")
        formInput.value=cadena;
        console.log(cadena);
        document.getElementById("accomodateForm").submit();
    }
}

qrScanner.start();
beep();