

function getTopWords() {
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            var resp = xhr.response.replace(/[\[\]()]/g, '').split(',');
            var x = document.getElementById("topwords");
            var i;
            x.innerText = '';
            for (i = 0; i < resp.length / 3; i++) {
                x.innerText += resp[i*3] + ': ';
                x.innerText += resp[i*3 + 1];
                x.innerText += resp[i*3 + 2] + '\n';
            }
        }
    };
    var x = document.getElementById("top");
    var body = 'top_n=' + x.elements[0].value;
    xhr.open('GET', ' http://localhost:8080?' + body, false);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send();
}


function genPreproc() {
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            var but = document.getElementsByClassName("gen_button");
            but.style.display = "none";
            const path = '/home/laneesra/PycharmProjects/speech_db/';
            var resp = xhr.response.split(';');
            var table = document.getElementById("table");
            table.innerHTML = '';

            for (i = 0; i < resp.length; i++) {
                var row = table.insertRow(0);
                var col = row.insertCell(0);
                var src = resp[i].substr(path.length);

                //col.innerHTML = src;
                if (src != '') {
                    col.innerHTML = '<h6>' + src + '</h6><div class="audio-player wow fadeInUp" align="center">\n' +
                        '<audio preload="auto" controls>\n' +
                        '<source src=\"' + src + '\"></audio></div>';
                }
            }
        }
    };
    var x = document.getElementById("preproc");
    var data = document.getElementById("dataset");
    var selected = data.options[data.selectedIndex].value;
    var body = 'preproc_n=' + x.elements[0].value + '&dataset=' + selected;
    xhr.open('GET', ' http://localhost:8080?' + body, false);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send();
}

function getTranscript() {
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            return xhr.response;
        }
    }
    var body = 'get_trans=1';
    xhr.open('GET', ' http://localhost:8080?' + body, false);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send();
}

function addSpeaker() {
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            alert('Запись добавлена');
        }
    }
    var x = document.getElementById("add");
    params = x.elements;
    var body = 'lastname=' + params[0].value + '&firstname=' + params[1].value + '&patronomic=' + params[2].value + '&path=' + params[5].value + '&transcription=' + params[6].value;
    xhr.open('POST', ' http://localhost:8080', false);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(body);
}

function identSpeaker() {
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            var resp = xhr.replace('/[\[,\],\(,\)]+/','');
            alert(resp);
        }
    }
    var els = document.getElementById("speakerNum");
    var choice;
    for (var i=0; i<els.length; i++){
        if ( els[i].checked ) {
            choice = els[i].value;
            alert(choice);

            break;
        }
    }
    var body = 'id=' + choice;
    xhr.open('GET', ' http://localhost:8080?' + body, false);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send();
}