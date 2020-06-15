// For localhost
// var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port); 

// For Heroku
// var socket = io.connect('//chatapp-0.herokuapp.com/socket.io/?EIO=4&transport=websocket'); 
var socker = io();

document.addEventListener('DOMContentLoaded', () => {
    const message_template = Handlebars.compile(document.querySelector('#message_template').innerHTML);
    const room_template = Handlebars.compile(document.querySelector('#room_template').innerHTML);

    //#region VERIFIED START
    if (localStorage.getItem('alias') !== null) {
        document.querySelector('#profile-alias').innerHTML = localStorage.getItem('alias');
        document.querySelector('#login').hidden = true;
        document.querySelector('#page').hidden = false;
    }

    if (localStorage.getItem('room') === null) {
        localStorage.setItem('room', 'general');
    }
    document.querySelector('#room').innerHTML = localStorage.getItem('room');
    //#endregion

    //#region MESSAGES FOR ACTUAL ROOM
    const request = new XMLHttpRequest();
    request.open('POST', '/ajax/chats/');
    const data = new FormData();
    data.append('room', localStorage.getItem('room'));
    request.send(data);
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        data.rooms.forEach(r => {
            const room = room_template({
                'name': r
            });
            // Add room element to the list
            document.querySelector('#rooms').innerHTML += room;
        });
        data.messages.forEach(m => {
            const message = message_template({
                'alias': m.alias,
                'message': m.message
            });
            // Add message element to the chat
            document.querySelector('#messages').innerHTML += message;
            document.querySelector('#chat-area').scrollTo(0, document.querySelector('#chat-area').scrollHeight);
        });
    };
    //#endregion

    socket.on('connect', () => {
        //#region SEND ROOM
        document.querySelector('#rooms').addEventListener('click', event => {
            localStorage.setItem('room', event.target.innerHTML);
            document.querySelector('#room').innerHTML = localStorage.getItem('room');

            const request = new XMLHttpRequest();
            request.open('POST', '/ajax/chats/');
            const data = new FormData();
            data.append('room', event.target.innerHTML);
            request.send(data);

            request.onload = () => {
                const data = JSON.parse(request.responseText);
                document.querySelector('#rooms').innerHTML = '';
                document.querySelector('#messages').innerHTML = '';

                data.rooms.forEach(r => {
                    const room = room_template({
                        'name': r
                    });
                    // Add room element to the list
                    document.querySelector('#rooms').innerHTML += room;
                });
                data.messages.forEach(m => {
                    const message = message_template({
                        'alias': m.alias,
                        'message': m.message
                    });
                    // Add message element to the chat
                    document.querySelector('#messages').innerHTML += message;
                    document.querySelector('#chat-area').scrollTo(0, document.querySelector('#chat-area').scrollHeight);
                });
            };
        });
        //#endregion

        //#region SEND MESSAGE
        document.querySelector('#send').onclick = () => {
            const message = document.querySelector('#new_message').value.trim();
            // clean new_message textarea
            document.querySelector('#new_message').value = '';
            document.querySelector('#new_message').focus();
            if (message === ''){
                return false;
            }
            // send message to server
            socket.emit('message_sent', {
                'alias': localStorage.getItem('alias'),
                'message': message,
                'room': localStorage.getItem('room')
            });
        };
        //#endregion
    }); 

    //#region SOCKET MESSAGE_RECEIVED
    socket.on('message_received', data => {
        if (data.room === localStorage.getItem('room')){
            const message = message_template({
                'alias': data.alias,
                'message': data.message
            });
            // Add message element to the chat
            document.querySelector('#messages').innerHTML += message;
            // Scroll down
            document.querySelector('#chat-area').scrollTo(0, document.querySelector('#chat-area').scrollHeight);
        }
    })
    //#endregion

    //#region PROFILE IMG
    document.querySelector('#profile-img').onclick = () => {
        alert('UPS! This function will be available soon!');
    };
    //#endregion

    //#region KEYS
    document.querySelector('#new_message').onkeydown = k_down => {
        if ((k_down.code === 'Enter') && (k_down.shiftKey === true)) {
            document.querySelector('#new_message').onkeyup = k_up => {
                if ((k_up.code === 'Enter') && (k_up.shiftKey === true)){
                    document.querySelector('#send').onclick();
                }
            };
            return false;
        }
        if (k_down.code === 'Enter'){
            document.querySelector('#new_message').onkeyup = k_up => {
                if (k_up.code === 'Enter'){
                    document.querySelector('#send').onclick();
                }
            };
            return false;
        }
    };
    //#endregion

    //#region LOGIN BEHAVIOUR
    document.querySelector('#login_start').onclick = () => {
        // Take alias value
        const alias = formatString(document.querySelector('#login_alias').value);
        // console.log('Alias formatted: "'+ alias +'"');

        if (alias === '') {
            alert('User alias is invalid!.\nPlease, choose another one.\nRemember not to include strange characters: keep the alias simple!');
        } else {
            // console.log(alias);

            const request = new XMLHttpRequest();
            request.open('POST', '/login/');
            const data = new FormData();
            data.append('alias', alias);
            request.send(data);
            request.onload = () => {
                const data = JSON.parse(request.responseText);
                if (!data.alias_ok){
                    alert('Ups! Alias "'+alias+'" already taken!\nChoose another one, please.');
                } else {
                    // console.log(alias,'has logged in');
                    localStorage.setItem('alias', alias);
                    document.querySelector('#profile-alias').innerHTML = alias;
                    document.querySelector('#login').hidden = true;
                    document.querySelector('#page').hidden = false;
                }
            };
        }
    };
    //#endregion
    
    //#region LOGOUT BEHAVIOUR
    document.querySelector('#profile-exit').onclick = () => {
        const alias = localStorage.getItem('alias');

        const request = new XMLHttpRequest();
        request.open('POST', '/logout/');

        request.onload = () => {
            localStorage.removeItem('alias');
            document.querySelector('#page').hidden = true;
            document.querySelector('#login').hidden = false;
        };
            
        const data = new FormData();
        data.append('alias', alias);
        request.send(data);  
    };
    //#endregion

});

formatString = (s) => {
    s = s.toLowerCase().replace(/[\s$!@#~`%^&+=|(){}[<>\-\]\/\*\\]/ig, "").trim().slice(0,15);
    return s;
}
// window.alert = function(message){
    
// }