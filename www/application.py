import sys

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = 'My_Super?Secret_Key987'
socketio = SocketIO(app)


##############################################################
# Users
users = []

##############################################################
# Channels
channels_messages = [
    [
        
    ]
]
channels_names = [
    'general'
]

    # print(f'\n\n \n', file=sys.stderr)

##############################################################
##############################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main.html', actual_channel='general', channels_names=channels_names, channels_messages=channels_messages[0])


@app.route("/ajax/channel/", methods=["POST"])
def channel():
    selected_channel = request.form.get('selected_channel')
    print(f'\n\n Selected channel: {selected_channel}\n', file=sys.stderr)

# User control
@app.route("/login/", methods=["POST"])
def login():
    if request.method == "POST":
        # Recuperamos el alias que el usuario quiere tener
        user_alias = request.form.get('user_alias')
        # Estandarizamos el alias
        user_alias = format_user_alias(user_alias)

        if user_alias_is_available(user_alias):
            add_user_alias(user_alias)
            return jsonify({'alias_ok': True})
        return jsonify({'alias_ok': False})
    return False

@app.route("/logout/", methods=['POST'])
def logout():
    user_alias = request.form.get('user_alias')
    # Estandarizamos el alias
    user_alias = format_user_alias(user_alias)

    users.remove(user_alias)
    return jsonify({'status': True})


# SocketIO methods
@socketio.on('message_sent')
def message_sent(data):
    print(f'\n\n Se recibe: {data} \n', file=sys.stderr)

    channels_names.index(data['channel'])
    print(f'\n\n Se encontró canal {data["channel"]} en índice {channels_names.index(data["channel"])} \n', file=sys.stderr)
    
    # guardamos el mensaje entrante en el canal que corresponda
    channels_messages[channels_names.index(data["channel"])].append({data['user_alias']: data['message']})

    print(f'\n\n Ahora el canal general tiene: {channels_messages[0]} \n', file=sys.stderr)

    emit('message_received', data, broadcast=True)

##############################################################
##############################################################
##############################################################

def user_alias_is_available(alias):
    if (alias != None):
        alias.strip()
        if alias != '':
            if alias in users:
                return False
            return True
    return False
        
def add_user_alias(alias):
    users.append(alias)

def format_user_alias(alias):
    return alias.lower()

@app.route("/register/", methods=["GET", "POST"])
def register():
    print(f'\n\nIngresamos a "register" por {request.method}\n', file=sys.stderr)

    if request.method == "GET":
        return render_template("register.html", message="")
    elif request.method == "POST":
        # tomar datos
        user_fullname = request.form.get('user_fullname')
        user_email = request.form.get('user_email')
        user_password = request.form.get('user_password')

        # Intentar meterlo a la base de datos. Corroborar si el email ya existe
        user = db.execute("SELECT user_email FROM users WHERE (users.user_email = :user_email)",
        {"user_email": user_email}).fetchone()
        # si existe ya un usuario con el mismo email
        if user:
            # No puede registrarse
            return render_template("register.html", message="Error al registrar usuario. Email ya existente")
        # sino
        else:
            print(f"{user_fullname}, {user_email}, {user_password}", file=sys.stderr)
            db.execute("INSERT INTO users (user_fullname, user_email, user_password) VALUES (:user_fullname, :user_email, :user_password)",
            {"user_fullname": user_fullname, "user_email": user_email, "user_password": user_password})
            try:
                db.commit()
                session['user_email'] = user_email
                return render_template("index.html", user_email=user_email)
            except:
                return render_template("error.html", message="Error al registrar usuario. Error de BDD.")