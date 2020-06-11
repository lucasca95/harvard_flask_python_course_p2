var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port); 


document.addEventListener('DOMContentLoaded', () => {
    
    const message_template = Handlebars.compile(document.querySelector('#message_template').innerHTML);
    
    var select_alias = document.querySelector('#select_alias');
    var my_nav = document.querySelector('#my_nav');
    const btn_alias = document.querySelector('#btn_alias');
    const btn_send_message = document.querySelector('#btn_send_message');
    let actual_channel = 'general';
    
    check_user_alias();    

    btn_alias.onclick = () => {
        const user_alias = document.querySelector('#user_alias').value.toLowerCase();

        const request = new XMLHttpRequest();
        // // Hacemos un request a /login/ por POST
        request.open('POST', '/login/');

        const data = new FormData();
        data.append('user_alias', user_alias);
        request.send(data);

        // // Al recibir la response...
        request.onload = () => {
            const data = JSON.parse(request.responseText);
            // alert('Se recibe alias_ok: "' + data.alias_ok + '"');
            if (data.alias_ok) {
                localStorage.setItem('user_alias', user_alias);
                check_user_alias();
            } else {
                alert('ERROR: Invalid or already taken User Alias. \n\n     Please, try again with another one!\n\n');
            }
        };
    };



    //#region btn_logout
    document.querySelector('#btn_logout').onclick = () => {
        const request = new XMLHttpRequest();
        // Hacemos un request a /logout/ por POST
        request.open('POST', '/logout/');
        const data = new FormData();
        data.append('user_alias', localStorage.getItem('user_alias'));
        request.send(data);

        // limpiar campo de texto del alias
        document.querySelector('#user_alias').value = '';
        // eliminar user_alias del localStorage
        localStorage.removeItem('user_alias');
        // refrescar menu alias
        check_user_alias();
    };
    //#endregion

    //#region socket on connect
    socket.on('connect', () => {
        btn_send_message.onclick = () => {
            const aux_message = document.querySelector('#message').value.trim();
            console.log(aux_message);
            
            if (document.querySelector('#message').value.trim() === ''){
                return false;
            }

            // enviar mensaje al servidor
            socket.emit('message_sent', {
                'user_alias':localStorage.getItem('user_alias'),
                'message': document.querySelector('#message').value.trim(),
                'channel': actual_channel
            });
            document.querySelector('#message').value = '';
        };
    }); 
    //#endregion

    //#region socket message_received
    socket.on('message_received', data => {
        // Get the message info
        const message = message_template({
            'user_alias': data.user_alias,
            'message': data.message
        });
        // Add message element to the chat
        document.querySelector('#messages').innerHTML += message;
    })
    //#endregion

    function check_user_alias(){
        let my_user_alias = localStorage.getItem('user_alias');

        // Si no tengo un user_alias aún...
        if (my_user_alias === null) {
            // Definir un user_alias
            console.log('user_alias not defined yet');
            my_nav.hidden = true;
            select_alias.hidden = false;
        } else {
            console.log('Actual user_alias "' + my_user_alias + '"');
            document.querySelector('#welcome').innerHTML = 'Hi, ' + my_user_alias + '! ' + document.querySelector('#welcome').innerHTML;
            my_nav.hidden = false;
            select_alias.hidden=true;
        }
    }

});
