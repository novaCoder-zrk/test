from flask import Flask, request
from flask_cors import CORS
from flask.views import MethodView
from PIL import Image
import base64
import io
import time

app = Flask(__name__)
CORS().init_app(app)


@app.route('/')
def hello_world():
    return 'Welcome!'


class MessageApi(MethodView):
    def post(self):
        data = request.json
        message = data.get('message')

        # time.sleep(5000)

        with open('test.png', 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        reply = '你说：“' + message + '”。 这是一个 [链接](http://example.com)'
        return {
            'status': 'success',
            'reply': reply,
            'image': img_base64
        }


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
