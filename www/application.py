import sys

from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
            
app.config["SECRET_KEY"] = 'My_Super?Secret_Key987'

if True:
    app.config["ENV"] = 'production'
else:
    app.config["ENV"] = 'development'
    app.config["DEBUG"] = True

socketio = SocketIO(app)


##############################################################
chat_limit = 100
mydebug = 0

##############################################################
# Users
users = []

##############################################################
# Rooms
room_messages = [
    [
        {
            'alias': 'Lucas',
            'message': 'Hola! Cómo estás? Sentite libre de probar el chat con quien gustes!'
        },
        {
            'alias': 'Lucas',
            'message': 'Seamos siempre respetuosos y evitemos usar expresiones dañinas u ofensivas. Muchas gracias!'
        }
    ],
    [
        {
            'alias': 'Lucas',
            'message': 'Este es el canal de música.'
        },
        {
            'alias': 'Lucas',
            'message': 'Lo agregué como segundo canal porque la música es mi hobby favorito.'
        }
    ]
]
room_names = [
    'general',
    'música'
]

    # print(f'\n\n \n', file=sys.stderr)

##############################################################
##############################################################
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/clean/m/', methods=['GET'])
def clean_m():
    for r_m in room_messages:
        r_m.clear()
    return redirect(url_for('index'))

@app.route('/clean/r/', methods=['GET'])
def clean_r():
    room_names.clear()
    room_names.append('general')
    room_messages.clear()
    room_messages.append([])
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

    if (mydebug):
        print(f'\n\nCantMessages: {len(room_messages[room_names.index(aux_room)])}\n{room_messages[room_names.index(aux_room)]}\n', file=sys.stderr)
    if (mydebug):
        print(f'\n\n Ahora la sala {aux_room} tiene:\n', file=sys.stderr)
        for m in room_messages[0]:
            for k,v in m.items():
                print(f'\n--{k}: {v}', file=sys.stderr)

    emit('message_received', {'alias':aux_alias, 'message':aux_message, 'room': aux_room}, broadcast=True)

@socketio.on('room_sent')
def room_sent(data):
    room_name = data['room_name']
    print(f'\n\n {data}\n', file=sys.stderr)

    if room_name_is_available(room_name):
        add_room(room_name)
        emit('room_received', {'status': True, 'room_name': room_name}, broadcast=True)
        return False
    emit('room_received', {'status': False, 'room_name': room_name}, broadcast=True)

##############################################################
##############################################################
##############################################################

def alias_is_available(alias):
    if alias in users:
        return False
    return True

def room_name_is_available(room_name):
    if room_name in room_names:
        return False 
    return True


def add_alias(alias):
    if mydebug:
        print(f'\nAdding alias "{alias}"\n', file=sys.stderr)
    users.append(alias)

def add_room(room_name):
    if mydebug:
        print(f'\nAdding room "{room_name}"\n', file=sys.stderr)
    room_names.append(room_name)
    room_messages.append([])


def delete_alias(alias):
    if mydebug:
        print(f'\nDeleting alias "{alias}"\n', file=sys.stderr)
    users.remove(alias)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=80)