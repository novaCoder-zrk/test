import random
from sql_tool import *


def generate_verify_code():
    code_list=[]
    for i in range(6):
        state=random.randint(1,3)
        if state==1:
            first_kind=random.randint(65,90)
            random_uppercase=chr(first_kind)
            code_list.append(random_uppercase)
        elif state==2:
            second_kinds=random.randint(97,122)
            random_lowercase=chr(second_kinds)
            code_list.append(random_lowercase)
        elif state==3:
            third_kinds=random.randint(0,9)
            code_list.append(str(third_kinds))
    verification_code="".join(code_list)
    print(verification_code)
    return verification_code







def check_verify_code_register(username, verify_code):
    last_verify_code = select_item('register_waiting', 'user_name', username, 'verify_code')
    print(last_verify_code)
    if last_verify_code is None:
        return False

    last_verify_time = select_item('register_waiting', 'user_name', username, 'verify_time')
    print(last_verify_time)
    dt_now = datetime.datetime.now()
    diff = dt_now - last_verify_time

    print(dt_now)
    if diff < datetime.timedelta(minutes=5):
        print("时间差小于5分钟")
        if verify_code == last_verify_code:
            # 让认证码失效
            new_verify_time = last_verify_time - datetime.timedelta(minutes=10)
            update_item('register_waiting', 'user_name', username, 'verify_time', new_verify_time)
            print("认证成功")
            return True
        else:
            print("认证失败")

    else:
        print("时间差大于等于5分钟")

    return False

def check_verify_code(username, verify_code):
    last_verify_code = select_item('account', 'user_name', username, 'verify_code')
    print(last_verify_code)
    if last_verify_code is None:
        return False

    last_verify_time = select_item('account', 'user_name', username, 'verify_time')
    print(last_verify_time)
    dt_now = datetime.datetime.now()
    diff = dt_now - last_verify_time

    print(dt_now)
    if diff < datetime.timedelta(minutes=5):
        print("时间差小于5分钟")
        if verify_code == last_verify_code:
            # 让认证码失效
            new_verify_time = last_verify_time - datetime.timedelta(minutes=10)
            update_item('account', 'user_name', username, 'verify_time', new_verify_time)
            print("认证成功")
            return True
        else:
            print("认证失败")
    else:
        print("时间差大于等于5分钟")

    return False

#code = get_verify_code('user1')
#check_verify_code('user1','cof7Wy')