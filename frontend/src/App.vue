<template>
    <div class="container">
        <div class="chat">
            <div v-for="(message, index) in messages" :key="index" class="message" :class="message.side">
                <img class="avatar" :src="message.side === 'right' ? userAvatar : botAvatar" alt="Avatar" />
                <img v-if="message.image" :src="message.image" alt="Image" />
                <div class="content" v-html="message.content"></div>
                <div v-if="isLoading && message.side === 'right' && index === messages.length - 1" class="loader"></div>
            </div>
        </div>
        <div class="send-box">
            <input type="text" v-model="input" @keydown.enter="sendMessage" class="send-input" placeholder="Input your message..."/>
            <button @click="sendMessage" class="send-button">Chat</button>
        </div>
    </div>
</template>


<script>
import axios from 'axios';
import MarkdownIt from 'markdown-it';
const md = new MarkdownIt();

export default {
    data() {
        return {
            input: '',
            messages: [],
            isLoading: false,
            userAvatar: '/png/user.png',
            botAvatar: '/png/bot.png',
        }
    },
    methods: {
        async sendMessage() {
            const message = this.input;
            this.input = '';
            if (!message) return;
            this.messages.push({ side: 'right', content: message });
            this.isLoading = true;
            this.$nextTick(this.scrollToBottom);
            await this.chatbotReply(message);
            this.isLoading = false;
        },
        async chatbotReply(message) {
            try {
                const requestPromise = axios.post('http://127.0.0.1:16161/messages', {
                    message
                });

                const timeoutPromise = new Promise((_, reject) => {
                    setTimeout(() => reject('No response, please retry.'), 5000);
                });

                const response = await Promise.race([requestPromise, timeoutPromise]);

                if (typeof response === 'string') {
                    throw response;
                }

                const reply = this.markdownToHtml(response.data.reply);
                const image = response.data.image ? 'data:image/png;base64,' + response.data.image : null;
                this.messages.push({ side: 'left', content: reply, image });
                this.$nextTick(() => {
                    this.$nextTick(this.scrollToBottom);
                });
                return { reply, image };
            } catch (error) {
                console.error(error);
                this.sendMessage();
                return { reply: error, image: null };
            }
        },
        markdownToHtml(markdownText) {
            return md.render(markdownText);
        },
        scrollToBottom() {
            const chat = this.$el.querySelector('.chat');
            chat.scrollTop = chat.scrollHeight;
        }
    }
}
</script>

<style>
* {
    box-sizing: border-box;
}

html, body {
    height: 100%;
    margin: 0;
    padding: 0;
}

.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 10px;
}

.container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 90%;
    margin: 0 auto;
    padding: 20px 10px;
    background-color: #fff;
    font-size: 18px;
}

.chat {
    flex-grow: 1;
    overflow-y: auto;
    margin-bottom: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #f6f8fa;
}

.message {
    margin-bottom: 10px;
    display: flex;
    flex-direction: row;
    align-items: start;
}

.message img {
    max-width: 50%;
    height: auto;
}

.message .content {
    padding: 10px;
    border-radius: 5px;
    font-family: Arial, sans-serif;
    width: fit-content;
    max-width: 90%;
}

.message.right {
    justify-content: flex-end;
}

.message.right .avatar {
    order: 2;
    margin-left: 10px;
    margin-right: 0;
}

.message.right .content {
    order: 1;
    color: #1E88E5;
    display: inline-block;
    background-color: #1E88E5;
    color: white;
}

.message.left .content {
    color: #333;
    display: inline-block;
    background-color: #eee;
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

.loader {
    border: 8px solid #f3f3f3;
    border-radius: 50%;
    border-top: 8px solid blue;
    width: 40px;
    height: 40px;
    animation: spin 2s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

</style>
