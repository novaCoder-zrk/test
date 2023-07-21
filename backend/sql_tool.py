import mysql.connector

# 连接 MySQL 数据库
db = mysql.connector.connect(
    host="54.206.93.57",
    user="remote",
    password="chatbotremote230718",
    database="mysql"
)

# 插入一条新记录
def insert_invitecode(code):
    cursor = db.cursor()
    sql = "INSERT INTO account (invitecode)  VALUES  (%s)"
    val = (code,)
    cursor.execute(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")


def insert_user(code, user_name, password, email):
    cursor = db.cursor()
    sql = "UPDATE account SET user_name=%s, password=%s, email=%s WHERE invitecode = %s"
    val = (user_name, password, email, code)
    cursor.execute(sql, val)
    db.commit()
    print(cursor.rowcount, "record updated.")


def insert_register(user_name, email, verify_code, verify_time):
    cursor = db.cursor()
    sql = "REPLACE INTO register_waiting (user_name, email, verify_code, verify_time)  VALUES  (%s, %s, %s, %s)"
    val = (user_name, email, verify_code, verify_time)
    cursor.execute(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")


def has_item(my_table, col, value):
    cursor = db.cursor()
    sql = "SELECT  COUNT(*) FROM " + my_table + " WHERE " + col + " = %s"
    val = (value,)
    cursor.execute(sql, val)
    result = cursor.fetchone()[0]
    #result = cursor.fetchall()[0]
    if result > 0:
        return True


def select_item(my_table, key_col, key_value, col):
    cursor = db.cursor()
    sql = "SELECT " + col + " FROM " + my_table + " WHERE " + key_col + " = %s"
    val = (key_value,)
    cursor.execute(sql, val)
    #result = cursor.fetchone()[0]
    result = cursor.fetchone()[0]
    return result

def update_item(my_table, key_col, key_value, col, value):
    cursor = db.cursor()
    sql = "UPDATE " + my_table + " SET " + col + " = %s " + "WHERE " + key_col + " = %s"
    val = (value, key_value)
    cursor.execute(sql, val)
    db.commit()
    print(cursor.rowcount, "record updated.")

def check_password(user_name,password):
    cursor = db.cursor()
    sql = "SELECT  invitecode FROM  account WHERE user_name = %s and password = %s"
    val = (user_name,password)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    return result

# if_has_item("account", "email", "temp@gmail.com")

#select_item('account', 'invitecode', 'INV001', 'user_name')
