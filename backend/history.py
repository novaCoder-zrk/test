import json
import os
from sql_tool import db
from datetime import datetime
import glob
import re

def save_historyfordays(invite_code, q, a):
    cursor = db.cursor()

    current_month = datetime.now().strftime('%Y%m')

    table_name = f"chat_history_{current_month}"

    cursor.execute(
        f"SELECT count(*) FROM information_schema.TABLES WHERE (TABLE_SCHEMA = 'mysql') AND (TABLE_NAME = '{table_name}')")
    result = cursor.fetchone()[0]

    if result == 0:
        cursor.execute(f"""
        CREATE TABLE {table_name} (
            chat_date DATE NOT NULL,
            invite_code VARCHAR(255) NOT NULL,
            question TEXT,
            answer TEXT
        );
        """)

    sql = f"INSERT INTO {table_name} (chat_date, invite_code, question, answer) VALUES (%s, %s, %s, %s)"
    chat_date = datetime.now().strftime('%Y-%m-%d')  # get current date
    val = (chat_date, invite_code, q, a)
    cursor.execute(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")


def save_history(file, q, a):
    folder_path = "./history"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = './history/'+ file
    try:
        with open(file_path, 'r') as f:
            chat_history = json.load(f)

        print(chat_history)
        if chat_history is None:
            chat_history = []

    except FileNotFoundError:
        chat_history = []
    except json.decoder.JSONDecodeError:
        chat_history = []

    new_chat = {'q': q, 'a': a}
    chat_history.append(new_chat)
    print(chat_history)

    with open(file_path, 'w') as f:
        json.dump(chat_history, f)


def load_history(filename):
    folder_path = "./history"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = './history/' + filename
    try:
        with open(file_path, 'r') as f:
            chat_history = json.load(f)
        if chat_history is None:
            chat_history = []
    except FileNotFoundError:
        chat_history = []
    except json.decoder.JSONDecodeError:
        chat_history = []

    return chat_history

def load_history_list(username):
    folder_path = "./history"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return []

    file_names = []
    # 使用 glob 模块匹配文件夹下的所有文件
    files = glob.glob(os.path.join(folder_path, '*'))
    for file in files:
        if os.path.isfile(file):
            file_names.append(os.path.basename(file))
    chat_lists = []
    for name in file_names:
        if username in name:
            date = re.search(r'\_(.*?)\.', name).group(1)
            if date == None or len(date) != 14:
                continue
            chat_lists.append(date[0:4]+"/"+date[4:6]+"/"+date[6:8] + " " + date[8:10] + ":" + date[10:12] + ":" + date[12:14])

    return chat_lists


def delete_chat_log(file_name):
    folder_path = "./history"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = './history/' + file_name

    if os.path.exists(file_path):
        os.remove(file_path)
        print("file removed")
    else:
        print("failure")


#