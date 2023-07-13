from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from chatbot import ChatbotBackend
from flask_socketio import SocketIO, emit
from flask.views import MethodView
import pandas as pd
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from email_sender import send_verify_code, sending
from verify_code_handler import check_verify_code, generate_verify_code, check_verify_code_register
import datetime
from history import save_history, load_history
import pprint


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
    save_history(message['username'], message['data'], response)

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
        user_email = request.json.get('email')
        verify_code = request.json.get('verify_code')

        data = pd.read_excel('account.xlsx')
        match = data[data['invitecode'] == invitecode]
        match_account = data[data['account'] == account]
        match_email = data[data['email'] == user_email]
        wl_df = pd.read_excel('register_waiting_list.xlsx')
        mask_wl = wl_df['account'] == account
        # 账户已经存在
        if not match_account.empty:
            return {'message': 'account has already exist', 'email_msg': ''}
        elif not match_email.empty:
            return {'message': 'email has been used', 'email_msg': ''}
        elif mask_wl.empty:
            # 账户不在waiting list中
            return {'message':'fail', 'email_msg': 'wrong verify code'}
        elif match.empty:
            # 邀请码不存在
            return {'message': 'invitation code does not exist', 'email_msg': ''}
        else:
            row = match.iloc[0]
            if pd.isnull(row['account']) and pd.isnull(row['password']) and pd.isnull(row['email']):
                # 邀请码没有被使用
                if check_verify_code_register(account, verify_code):
                    # 检查验证码，并使它过期
                    data.loc[data['invitecode'] == invitecode, ['account', 'password', 'email']] = [account, password, user_email]
                    data.to_excel('account.xlsx', index=False)
                else:
                    return {'message': 'fail', 'email_msg': 'wrong verify code'}
            else:
                return {'message': 'invitation code has been used', 'email_msg': ''}
        # 验证码
        return {'message': 'Registration successful', 'email_msg': ''}


def mask_email_address(email):
    # 获取邮箱中 @ 符号的位置
    at_index = email.find('@')

    # 判断 @ 符号前的字符数是否满足条件
    if at_index >= 4:
        # 获取 @ 符号前的最后 4 个字符
        last_4_chars = email[at_index - 4:at_index]
        # 将最后 4 个字符替换为 *
        masked_email = email.replace(last_4_chars, '*' * 4, 1)
    else:
        # 只保留最高位字符，其余替换为 *
        masked_email = email[0].replace(email[0], '*') + email[1:at_index]
 # 输出：exa****@example.com
    return masked_email


# For reset password
class SendVerifyCodeApi(MethodView):
    def post(self):
        try:
            account = request.json.get('account')
            df = pd.read_excel('account.xlsx')
            mask_account = df["account"] == account
            mask_email = df['email'] == account
            user_data_account = df.loc[mask_account]
            user_data_email = df.loc[mask_email]

            if user_data_account.empty and user_data_email.empty:
                # 没有对应的账户
                response = {'message': 'fail'}
            elif not user_data_account.empty:
                my_account = user_data_account.loc[:, 'account'].values[0]
                my_email = user_data_account.loc[:, 'email'].values[0]
                send_verify_code(my_account)
                my_email = mask_email_address(str(my_email))
                response = {'message': 'success', 'email': my_email}
            else:
                my_account = user_data_email.loc[:, 'account'].values[0]
                my_email = user_data_email.loc[:, 'email'].values[0]
                send_verify_code(my_account)
                response = {'message': 'success', 'email': ""}

        except Exception as e:
            print('Error sending verify code email:', e)
            response = {'message': 'fail'}
        return response


# for register
class SendVerifyCodeByEmailApi(MethodView):
    def post(self):
        try:
            account = request.json.get('account')
            print(account)
            email = request.json.get('email')
            print(email)
            # 判断 account 和 email 是否都没有被使用
            df_account = pd.read_excel('account.xlsx')
            if not df_account[df_account['account'] == account].empty:
                print("account already exists")
                return {'message': 'fail', 'account_msg': 'account already exists', 'email_msg': ''}
            if not df_account[df_account['email'] == email].empty:
                print('email has been used')
                return {'message': 'fail', 'account_msg': '', 'email_msg': 'email has been used'}

            # 向register_waiting_list.xlsx 中添加项目
            df = pd.read_excel('register_waiting_list.xlsx')
            mask = df["account"] == account
            user_data = df[mask]

            if user_data.empty:
                print("true")
                df.loc[len(df), 'account'] = account
            mask = df["account"] == account
            df.loc[mask, 'email'] = email
            code = generate_verify_code()
            dt = datetime.datetime.now()  # 获取当前时间
            dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            df.loc[mask, 'verify_code'] = code
            df.loc[mask, 'verify_time'] = dt_str

            df.to_excel('register_waiting_list.xlsx', index=False)
            if not sending(email, code):
                return {'message': 'fail', 'account_msg': '', 'email_msg': 'e-mail sending failed'}

            response = {'message': 'success'}
            return response
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


class ChatHistory(MethodView):
    def post(self):
        username = request.json.get('username')
        chat_history = load_history(username)

        chat_data = []
        # 解析聊天记录
        for chat in chat_history:
            new_data = {'question': chat['q']}

            fig_path = None
            response = chat['a']
            if "#@@#" in response and response.endswith(".png"):
                response, fig_path = response.split("#@@#")
            img_base64 = None
            if fig_path is not None:
                with open("./img/" + fig_path, 'rb') as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

            new_data['response'] = response
            if img_base64 is not None:
                new_data['image'] = img_base64
            chat_data.append(new_data)
        return {'history': chat_data}



register_api = RegisterApi.as_view('register_api')
app.add_url_rule('/register', view_func=register_api, methods=['POST'])

login_api = LoginApi.as_view('login_api')
app.add_url_rule('/login', view_func=login_api, methods=['POST'])

verify_token_api = VerifyTokenApi.as_view('verify_token_api')
app.add_url_rule('/verifyToken', view_func=verify_token_api, methods=['POST'])

send_verify_code_api = SendVerifyCodeApi.as_view('send_verify_code_api')
app.add_url_rule('/sendVerifyCode', view_func=send_verify_code_api, methods=['POST'])

send_verify_code_by_email_api = SendVerifyCodeByEmailApi.as_view('send_verify_code_by_email_api')
app.add_url_rule('/sendVerifyCodeByEmail', view_func=send_verify_code_by_email_api, methods=['POST'])

reset_password_api = ResetPassword.as_view('reset_password_api')
app.add_url_rule('/resetPassword', view_func=reset_password_api, methods=['POST'])

chat_history_api = ChatHistory.as_view('chat_history_api')
app.add_url_rule('/chatHistory', view_func=chat_history_api, methods=['POST'])

if __name__ == '__main__':
    app.run()
    socketio.run(app)
