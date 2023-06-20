import time

from flask import Flask, request
from flask_cors import CORS
from flask.views import MethodView
import base64
import threading
from chatbot import ChatbotBackend
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")
chatbot = ChatbotBackend()


@app.route('/')
def hello_world():
    return 'Welcome!'


@socketio.on("connect")
def handle_connect():
    print("server has connected")


def timeOut():
    print("time out !!!!")
    emit('timeout', {'status': 'timeout'})


@socketio.on("message")
def handle_message(message):
    print(message)
    print(message['data'])
    response = chatbot.generate_response(message['data'])
    fig_path = None
    if "#@@#" in response and response.endswith(".png"):
        response, fig_path = response.split("#@@#")
    img_base64 = None
    if fig_path is not None:
        with open("./img/" + fig_path, 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    reply = {'status': 'success', 'question': message['data'], 'reply': response}
    if img_base64 is not None:
        reply['image'] = img_base64

    # reply = {'status': 'success', ,
    #          'reply': message['data']}
    emit('response', reply)


@socketio.on("disconnect")
def handle_disconnect():
    print("server has  disconnected!!!")


if __name__ == '__main__':
    app.run()
    socketio.run(app)
