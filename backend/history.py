import json
import os


def save_history(user, q, a):
    folder_path = "./history"  # 替换为你要创建的文件夹路径

    if not os.path.exists(folder_path):  # 检测文件夹是否存在
        os.makedirs(folder_path)  # 创建文件夹

    file_path = './history/'+user+'_history.json'
    try:
        with open(file_path, 'r') as f:
            chat_history = json.load(f)

        print(chat_history)
        if chat_history is None:
            chat_history = []

    except FileNotFoundError:
        chat_history = []
    except json.decoder.JSONDecodeError:
        # 文件为空，返回空列表
        chat_history = []

    new_chat = {'q': q, 'a': a}
    chat_history.append(new_chat)
    print(chat_history)

    # 将新的聊天记录保存到JSON文件中
    with open(file_path, 'w') as f:
        json.dump(chat_history, f)


def load_history(user):
    folder_path = "./history"  # 替换为你要创建的文件夹路径

    if not os.path.exists(folder_path):  # 检测文件夹是否存在
        os.makedirs(folder_path)  # 创建文件夹

    file_path = './history/' + user + '_history.json'
    try:
        with open(file_path, 'r') as f:
            chat_history = json.load(f)
        if chat_history is None:
            chat_history = []
    except FileNotFoundError:
        chat_history = []
    except json.decoder.JSONDecodeError:
        # 文件为空，返回空列表
        chat_history = []

    return chat_history

#save_history("user1", "hello", "hello")

