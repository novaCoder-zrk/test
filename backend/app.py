from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from chatbot import ChatbotBackend
from flask_socketio import SocketIO, emit
from flask.views import MethodView
import pandas as pd
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from email_sender import send_verify_code
from verify_code_handler import check_verify_code

app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "your-secret-key"
jwt = JWTManager(app)

socketio = SocketIO(app, cors_allowed_origins="*")
chatbot = ChatbotBackend()

@app.route('/')
def hello_world():
    return 'Welcome!'


@socketio.on("connect")
def handle_connect():
    print("server has connected")


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

    emit('response', reply)


@socketio.on("disconnect")
def handle_disconnect():
    print("server has  disconnected!!!")


class LoginApi(MethodView):
    def post(self):
        account = request.json.get('account')
        password = request.json.get('password')

        data = pd.read_excel('account.xlsx')
        match = data[(data['account'] == account) & (data['password'] == password)]

        if not match.empty:
            invitecode = match.iloc[0]['invitecode']
            token = create_access_token(identity=invitecode)
            response = {'invitecode': invitecode, 'token': token}
        else:
            response = {'invitecode': 'default'}

        return response


class VerifyTokenApi(MethodView):
    @jwt_required()
    def post(self):
        return jsonify({"isValid": True})


class RegisterApi(MethodView):
    def post(self):
        invitecode = request.json.get('invitecode')
        account = request.json.get('account')
        password = request.json.get('password')
        email = request.json.get('email')

        data = pd.read_excel('account.xlsx')
        match = data[data['invitecode'] == invitecode]

        if match.empty:
            response = {'message': 'code does not exist'}
        else:
            row = match.iloc[0]
            if pd.isnull(row['account']) and pd.isnull(row['password']) and pd.isnull(row['email']):
                data.loc[data['invitecode'] == invitecode, ['account', 'password', 'email']] = [account, password, email]
                data.to_excel('account.xlsx', index=False)
                response = {'message': 'Registration successful'}
            else:
                response = {'message': 'code has been used'}

        return response


class SendVerifyCodeApi(MethodView):
    def post(self):
        try:
            account = request.json.get('account')
            df = pd.read_excel('account.xlsx')
            mask = df["account"] == account
            user_data = df[mask]

            if user_data.empty:
                # 没有对应的账户
                response = {'message': 'fail'}
            else:
                send_verify_code(account)
                response = {'message': 'success'}
        except Exception as e:
            print('Error sending verify code email:', e)
            response = {'message': 'fail'}
        return response


class ResetPassword(MethodView):
    def post(self):
        account = request.json.get('account')
        verify_code = request.json.get('verify_code')
        password = request.json.get('password')
        if check_verify_code(account, verify_code):
            df = pd.read_excel('account.xlsx')
            mask = df['account'] == account
            df.loc[mask, 'password'] = password
            df.to_excel('account.xlsx', index=False)
            return {'message': 'success'}

        return {'message': 'fail'}


register_api = RegisterApi.as_view('register_api')
app.add_url_rule('/register', view_func=register_api, methods=['POST'])

login_api = LoginApi.as_view('login_api')
app.add_url_rule('/login', view_func=login_api, methods=['POST'])

verify_token_api = VerifyTokenApi.as_view('verify_token_api')
app.add_url_rule('/verifyToken', view_func=verify_token_api, methods=['POST'])

send_verify_code_api = SendVerifyCodeApi.as_view('send_verify_code_api')
app.add_url_rule('/sendVerifyCode', view_func=send_verify_code_api, methods=['POST'])

reset_password_api = ResetPassword.as_view('reset_password_api')
app.add_url_rule('/resetPassword', view_func=reset_password_api, methods=['POST'])

if __name__ == '__main__':
    app.run()
    socketio.run(app)
