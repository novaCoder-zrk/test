from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from chatbot import ChatbotBackend
from flask_socketio import SocketIO, emit
from flask.views import MethodView
import pandas as pd
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from email_sender import sending
from verify_code_handler import check_verify_code, generate_verify_code, check_verify_code_register
import datetime
from history import save_history, load_history
from sql_tool import *
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
    data = pd.read_excel('account.xlsx')
    match = data[data['invitecode'] == message['username']]

    if not match.empty:
        user = match.iloc[0]
        if not pd.isnull(user['hourly_start_time']):
            hourly_start_time = datetime.datetime.strptime(user['hourly_start_time'], '%Y-%m-%d %H:%M:%S')
            if (datetime.datetime.now() - hourly_start_time).seconds < 3600:
                # within an hour
                if user['hourly_usage'] >= user['hourly_limit']:
                    emit('response', {'status': 'success', 'question': message['data'], 'reply': "This hour's balance exceeds the limit."})
                    return
                else:
                    user['hourly_usage'] += 1
            else:
                user['hourly_start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                user['hourly_usage'] = 1
        else:
            user['hourly_start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user['hourly_usage'] = 1

        if user['total_usage'] >= user['total_limit']:
            emit('response', {'status': 'success', 'question': message['data'], 'reply': "The account's balance exceeds the limit."})
            return
        else:
            user['total_usage'] += 1

        index_to_update = data.loc[data['invitecode'] == user['invitecode']].index
        if not index_to_update.empty:
            index_to_update = index_to_update[0]

            for column in user.keys():
                data.at[index_to_update, column] = user[column]
        else:
            print(f"No row found with invitecode = {user['invitecode']}")

        data.to_excel('account.xlsx', index=False)

    print(message)
    print(message['data'])

    # response = "temp"
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

        invitecode = check_password(account, password)
        if invitecode is not None:
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
        if has_item('account', 'user_name', account):
            # 账户已经存在
            print("account already exists")
            return {'message': 'account has already exist', 'email_msg': ''}
        if has_item('account', 'email', user_email):
            # 邮箱已经被使用
            print('email has been used')
            return {'message': 'email has been used', 'email_msg': ''}
        if not has_item('register_waiting', 'user_name', account):
            # waiting list中没有对应的account
            return {'message': 'fail', 'email_msg': 'wrong verify code'}
        if not has_item('account', 'invitecode', invitecode):
            # 邀请码不存在
            return {'message': 'invitation code does not exist', 'email_msg': ''}
        if select_item('account', 'invitecode', invitecode, 'user_name') != None:
            # 邀请码已经被使用
            return {'message': 'invitation code has been used', 'email_msg': ''}
        # 邀请码没有被使用
        if check_verify_code_register(account, verify_code): # 检查验证码，并使它过期
            # 将 用户名 密码 email 写入account表中
            insert_user(invitecode, account, password, user_email)
        else:
            return {'message': 'fail', 'email_msg': 'wrong verify code'}

        # 注册成功
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
            if has_item('account', 'user_name', account):
                # 输入的用户名存在
                code = generate_verify_code()
                dt_now = datetime.datetime.now()
                dt_str = dt_now.strftime('%Y-%m-%d %H:%M:%S')
                my_email = select_item('account', 'user_name', account, 'email')
                sending(my_email, code)

                update_item('account', 'user_name', account, 'verify_code', code)
                update_item('account', 'user_name', account, 'verify_time', dt_str)

                my_email = mask_email_address(str(my_email))
                response = {'message': 'success', 'email': my_email}

            elif has_item('account', 'email', account):
                my_email = account
                code = generate_verify_code()
                dt_now = datetime.datetime.now()
                dt_str = dt_now.strftime('%Y-%m-%d %H:%M:%S')
                sending(my_email, code)

                update_item('account', 'email', my_email, 'verify_code', code)
                update_item('account', 'email', my_email, 'verify_time', dt_str)
                response = {'message': 'success', 'email': ""}

            else:
                response = {'message': 'fail'}

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
            if has_item('account', 'user_name', account):
                print("account already exists")
                return {'message': 'fail', 'account_msg': 'account already exists', 'email_msg': ''}
            if has_item('account', 'email', email):
                print('email has been used')
                return {'message': 'fail', 'account_msg': '', 'email_msg': 'email has been used'}

            # 向register_waiting 中添加项目
            code = generate_verify_code() # 获取验证码
            dt = datetime.datetime.now()  # 获取当前时间
            dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            # 写入数据库
            insert_register(account, email, code, dt_str)

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
        if has_item('account', 'user_name', account):
            user_name = account
        elif has_item('account', 'email', account):
            my_email = account
            user_name = select_item('account','email', my_email,'user_name')
        else:
            return {'message': 'fail'}

        if check_verify_code(user_name, verify_code):
            update_item('account', 'user_name', user_name, 'password', password)
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
