<template>
    <div class="container">
        <div class="chat">
            <div v-for="(message, index) in messages" :key="index" class="message" :class="message.side">
                <div class="content" v-html="message.content"></div>
                <img v-if="message.image" :src="message.image" alt="Image" />
            </div>
        </div>
        <div class="send-box">
            <input type="text" v-model="input" @keydown.enter="sendMessage" class="send-input" placeholder="输入消息..."/>
            <button @click="sendMessage" class="send-button">发送</button>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import MarkdownIt from 'markdown-it'
const md = new MarkdownIt()

export default {
    data() {
        return {
            input: '',
            messages: []
        }
    },
    methods: {
        async sendMessage() {
            if (!this.input) return;
            this.messages.push({ side: 'right', content: this.input });
            const {reply, image} = await this.chatbotReply(this.input);
            this.messages.push({ side: 'left', content: reply, image });
            this.input = '';
        },
        async chatbotReply(message) {
            try {
                const requestPromise = axios.post('http://localhost:5000/messages', {
                    message
                });

                const timeoutPromise = new Promise((_, reject) => {
                    setTimeout(() => reject('后端暂时无响应，重新尝试中...'), 5000);
                });

                const response = await Promise.race([requestPromise, timeoutPromise]);

                if (typeof response === 'string') {
                    throw response;
                }

                const reply = this.markdownToHtml(response.data.reply);
                const image = 'data:image/png;base64,' + response.data.image;
                return { reply, image };
            } catch (error) {
                console.error(error);
                this.sendMessage();
                return { reply: error, image: null };
            }
        },
        markdownToHtml(markdownText) {
            return md.render(markdownText);
        }
    }
}
</script>

<style>
* {
    box-sizing: border-box;
}

.container {
    width: 100%;
    margin: 0 auto;
    padding: 20px 10px;
    background-color: #fff;
    font-size: 18px;
}

.login-panel {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

.login-form {
    width: 300px;
}

.chat {
    max-height: 500px;
    overflow-y: auto;
    margin-bottom: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #f6f8fa;
}

.send-box {
    display: flex;
    justify-content: space-between;
}

.message {
    margin-bottom: 10px;
    border-bottom: 1px solid #ccc;
}

.message .content {
    padding: 10px;
    border-radius: 5px;
    font-family: Arial, sans-serif;
}

.message.right .content {
    color: #1E88E5;
}

.message.left .content {
    color: #333;
}

.send-box {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
}

.send-input {
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 10px;
    font-size: 18px;
    margin-bottom: 10px;
    flex-grow: 1;
    height: 100%;
    margin-right: 10px;
}

.send-button {
    background-color: #1E88E5;
    color: #fff;
    border: none;
    border-radius: 5px;
    padding: 10px;
    cursor: pointer;
    font-size: 18px;
    width: 80px;
    height: 100%;
}
</style>
