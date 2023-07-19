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


insert_register('user1', 'pass2', 'bbb', '2023/7/1  12:18:33')