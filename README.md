# Project 2

Web Programming with Python and JavaScript

git pull && git add . && git commit -m '.' && git push && git push heroku master

--op 1
web: gunicorn --worker-class socketio.sgunicorn.GeventSocketIOWorker --log-file=- www.application:app

--op 2
web: gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker --log-file=- www.application:app