from flask import Flask
from flask_socketio import SocketIO, emit

socket = SocketIO()
def create_app():
    forum_index_name = "forum-articles-*"
    app = Flask(__name__)
    socket.init_app(app)
    routing(app)
    return app, socket    
