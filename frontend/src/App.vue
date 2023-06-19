<template>
    <div class="container">
        <div class="chat">
            <div v-for="(message, index) in messages" :key="index" class="message" :class="message.side">
                <img class="avatar" :src="message.side === 'right' ? userAvatar : botAvatar" alt="Avatar" />
                <img v-if="message.image" :src="message.image" alt="Image" />
                <div class="content" v-html="message.content"></div>
                <div>
                <div v-if=" isLoading===true && message.side === 'right' && index === messages.length - 1" class="loader"></div>
                <span v-if=" isLoading===true && message.side === 'right' && index === messages.length - 1" class="">{{loaderTip}}</span>
                </div>
            </div>
        </div>
        <div class="send-box">
            <input type="text" v-model="input" @keydown.enter="sendMessage" class="send-input" placeholder="Input your message..."/>
            <button @click="sendMessage" class="send-button">Chat</button>
        </div>
    </div>
</template>


<script setup>
import axios from 'axios';
import MarkdownIt from 'markdown-it';
const md = new MarkdownIt();
import io from 'socket.io-client';
import {ref} from "vue";
let loaderTip = ref("...");
let isLoading = ref(false);
let userAvatar = ref('/png/user.png');
let botAvatar =  ref('/png/bot.png');
let input = ref('');
let messages = ref([]);
let timerId;
let delay = 30000;
let socket = io.connect('http://127.0.0.1:16161');
let lastQuestion;
socket.on('connect', function() {
    console.log("connected！")
});

socket.on('response',function(msg){

    console.log(msg)
    if(msg.question !== lastQuestion)
        return;
    const image = msg.image ? 'data:image/png;base64,' + msg.image : null;
    messages.value.push({ side: 'left', content: msg.reply, image });
    isLoading.value = false;
    lastQuestion = "";
    clearTimeout(timerId);
});

socket.on('status',function(msg){
    console.log(msg)
    loaderTip.value = msg.status;
});

// timeout 由后端通知
socket.on('timeout',function(msg){
    console.log(msg)
    isLoading.value = false;
});
socket.on('disconnect', function() {

    console.log('已断开与服务器的连接');
});




function sendMessage() {
    const msg = input.value;
    input.value = '';
    lastQuestion = msg;
    if (!msg) return;
    messages.value.push({ side: 'right', content: msg });
    console.log("111")
    // loading
    loaderTip.value = "...";
    isLoading.value = true;

    chatbotReply(msg);
    console.log("22")
}

function myFunction() {
    console.log("定时器到期，执行函数");
    lastQuestion = "";
    messages.value.push({ side: 'left', content: "No response, please retry." });
    isLoading.value = false;
}

function chatbotReply(msg) {
    try {
        // 建立socket链接
        timerId = setTimeout(myFunction, delay);
        socket.connect();
        socket.emit('message', {"data": msg});
    } catch (error) {
        console.error(error);
        this.sendMessage();
    }
}

function markdownToHtml(markdownText) {
    return md.render(markdownText);
}

function scrollToBottom() {
    const chat = this.$el.querySelector('.chat');
    chat.scrollTop = chat.scrollHeight;
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

.loader_tip{

}
.loader {
    border: 4px solid #f3f3f3;
    border-radius: 50%;
    border-top: 4px solid blue;
    width: 20px;
    height: 20px;
    animation: spin 2s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

</style>
