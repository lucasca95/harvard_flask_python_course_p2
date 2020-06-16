import sys

from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')
            
app.config["SECRET_KEY"] = 'My_Super?Secret_Key987'

if False:
    app.config["ENV"] = 'production'
else:
    app.config["ENV"] = 'development'
    app.config["DEBUG"] = True

socketio = SocketIO(app)


##############################################################
chat_limit = 20
mydebug = 1

##############################################################
# Users
users = ['pedro', 'marta']

##############################################################
# Rooms
room_messages = [
    [
        {
            'alias': 'random',
            'message': 'Hola!'
        },
        {
            'alias': 'random',
            'message': 'Hay alguien?'
        }
    ],
    [
        {
            'alias': 'martina',
            'message': ':)'
        },
        {
            'alias': 'javier',
            'message': 'ola!'
        }
    ]
]
room_names = [
    'general',
    'facultad'
]

    # print(f'\n\n \n', file=sys.stderr)

##############################################################
##############################################################
@app.route('/', methods=['GET'])
def index():
    # return 'Funcionando'
    return render_template('index.html')

@app.route('/clean/', methods=['GET'])
def clean():
    for r_m in room_messages:
        r_m.clear()
    return redirect(url_for('index'))

@app.route('/ajax/chats/', methods=['POST'])
def chats():
    room = request.form.get('room')
    return jsonify({'messages': room_messages[room_names.index(room)], 'rooms': room_names})

##############################################################
##############################################################
##############################################################
# User control
@app.route("/login/", methods=["POST"])
def login():
    alias = request.form.get('alias')
    if alias_is_available(alias):
        add_alias(alias)
        return jsonify({'alias_ok': True})

    return jsonify({'alias_ok': False})

@app.route("/logout/", methods=['POST'])
def logout():
    alias = request.form.get('alias')
    delete_alias(alias)
    return jsonify(True)

@app.route("/users/", methods=['GET'])
def users_list():
    return jsonify(users)

##############################################################
##############################################################
##############################################################
# SocketIO methods
@socketio.on('message_sent')
def message_sent(data):
    aux_alias = data['alias']
    aux_message = data['message']
    aux_room = data['room']
    if (mydebug):
        print(f'\n\nAlias: {aux_alias}\nMessage: {aux_message}\nRoom: {aux_room}\n', file=sys.stderr)
    
    # save new message in the correct room
    room_messages[room_names.index(aux_room)].append({
        'alias': aux_alias,
        'message': aux_message
    })
    
    # save only the last "chat_limit" messages
    if (len(room_messages[room_names.index(aux_room)]) > chat_limit):
        room_messages[room_names.index(aux_room)] = room_messages[room_names.index(aux_room)][1:chat_limit+1] 

    if (not mydebug):
        print(f'\n\nCantMessages: {len(room_messages[room_names.index(aux_room)])}\n{room_messages[room_names.index(aux_room)]}\n', file=sys.stderr)
    if (not mydebug):
        print(f'\n\n Ahora la sala {aux_room} tiene:\n', file=sys.stderr)
        for m in room_messages[0]:
            for k,v in m.items():
                print(f'\n--{k}: {v}', file=sys.stderr)

    emit('message_received', {'alias':aux_alias, 'message':aux_message, 'room': aux_room}, broadcast=True)

##############################################################
##############################################################
##############################################################

def alias_is_available(alias):
    if alias in users:
        return False
    return True
        
def add_alias(alias):
    print(f'\nAdding alias "{alias}"\n', file=sys.stderr)
    users.append(alias)

def delete_alias(alias):
    print(f'\nDeleting alias "{alias}"\n', file=sys.stderr)
    users.remove(alias)

if __name__ == "__main__":
    for k,v in app.config.items():
        print(f'\n{k}: {v}')
    app.run(host='0.0.0.0', port=80)