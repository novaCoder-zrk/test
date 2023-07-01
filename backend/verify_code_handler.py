import random
import pandas as pd
import datetime



def generate_verify_code():
    code_list=[]
    for i in range(6):    #控制验证码的位数
        state=random.randint(1,3)   #生成状态码
        if state==1:
            first_kind=random.randint(65,90)   #大写字母
            random_uppercase=chr(first_kind)
            code_list.append(random_uppercase)
        elif state==2:
            second_kinds=random.randint(97,122)  #小写字母
            random_lowercase=chr(second_kinds)
            code_list.append(random_lowercase)
        elif state==3:
            third_kinds=random.randint(0,9)
            code_list.append(str(third_kinds))
    verification_code="".join(code_list)
    print(verification_code)
    return verification_code


def update_verify_code(username, verify_code):
    df = pd.read_excel('account.xlsx')
    mask = df['account'] == username

    if mask.empty:
        print("no match")
    else:
        dt = datetime.datetime.now()  # 获取当前时间
        print(dt)
        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        # print(dt_str)
        df.loc[mask, 'verify_code'] = verify_code
        df.loc[mask, 'verify_time'] = dt_str
        df.to_excel('account.xlsx', index=False)


def get_verify_code(username):
    code = generate_verify_code()
    update_verify_code(username, code)
    return code


def check_verify_code_register(username, verify_code):
    df = pd.read_excel('register_waiting_list.xlsx')
    mask = df["account"] == username
    user_data = df.loc[mask]
    last_verify_time = user_data['verify_time'].values[0]
    last_verify_time = datetime.datetime.utcfromtimestamp(last_verify_time.astype('O') / 1e9)

    print(last_verify_time)
    last_verify_code = user_data['verify_code'].values[0]
    print(last_verify_code)
    dt_now = datetime.datetime.now()
    diff = dt_now - last_verify_time
    if diff < datetime.timedelta(minutes=5):
        print("时间差小于5分钟")
        if verify_code == last_verify_code:
            # 让认证码失效
            new_verify_time = last_verify_time - datetime.timedelta(minutes=10)
            df.loc[mask, 'verify_time'] = new_verify_time
            df.to_excel('register_waiting_list.xlsx', index=False)

            print("认证成功")
            return True
        else:
            print("认证失败")

    else:
        print("时间差大于等于5分钟")

    return False

def check_verify_code(username, verify_code):
    df = pd.read_excel('account.xlsx')
    mask = df["account"] == username
    user_data = df.loc[mask]
    last_verify_time = user_data['verify_time'].values[0]
    last_verify_time = datetime.datetime.utcfromtimestamp(last_verify_time.astype('O') / 1e9)

    print(last_verify_time)
    last_verify_code = user_data['verify_code'].values[0]
    print(last_verify_code)
    dt_now = datetime.datetime.now()
    diff = dt_now - last_verify_time
    if diff < datetime.timedelta(minutes=5):
        print("时间差小于5分钟")
        if verify_code == last_verify_code:
            # 让认证码失效
            new_verify_time = last_verify_time - datetime.timedelta(minutes=10)
            df.loc[mask, 'verify_time'] = new_verify_time
            df.to_excel('account.xlsx', index=False)

            print("认证成功")
            return True
        else:
            print("认证失败")

    else:
        print("时间差大于等于5分钟")

    return False

#code = get_verify_code('user1')
#check_verify_code('user1','cof7Wy')