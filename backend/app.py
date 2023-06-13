import time

from flask import Flask, request
from flask_cors import CORS
from flask.views import MethodView
import base64

from chatbot import ChatbotBackend

app = Flask(__name__)
CORS().init_app(app)


@app.route('/')
def hello_world():
    return 'Welcome!'


chatbot = ChatbotBackend()


class MessageApi(MethodView):

    def post(self):
        data = request.json
        message = data.get('message')
        response = chatbot.generate_response(message)
        fig_path = None
        if "#@@#" in response and response.endswith(".png"):
            response, fig_path = response.split("#@@#")
        img_base64 = None
        if fig_path is not None:
            with open("./img/" + fig_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        reply = {'status': 'success', 'reply': response}
        if img_base64 is not None:
            reply['image'] = img_base64

        return reply


class LoginApi(MethodView):
    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')

        return {'authenticated': True}


message_api = MessageApi.as_view('message_api')
login_api = LoginApi.as_view('login_api')
app.add_url_rule('/messages', view_func=message_api, methods=['POST'])
app.add_url_rule('/login', view_func=login_api, methods=['POST'])
