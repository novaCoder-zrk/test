<template>
    <div class="chatpdf">
        <div class="back-icon-container">
            <img class="icon" @click="handleBack" src="../assets/back-white.svg" alt="go back" />
        </div>
        <div class="pannel">
            <div class="chatbotTitle">CHATBOT</div>
            <div class="sideList">
                <div  v-for="(chat_name, index) in chatLogs" :key="index" class="fileTitle" @click="handleClickChatLog(chat_name)">
                    {{chat_name}}
                </div>

            </div>
        </div>
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
    </div>
</template>


<script setup>
import {onMounted, onUpdated} from 'vue';
import axios from 'axios';
import MarkdownIt from 'markdown-it';
import io from 'socket.io-client';
import {ref} from "vue";
import { useRouter } from 'vue-router'

let loaderTip = ref("...");
let isLoading = ref(false);
let userAvatar = ref('/png/user.png');
let botAvatar =  ref('/png/bot.png');
let input = ref('');
let messages = ref([]);
let timerId;
let delay = 100000;
let chatLogs = ref([]);

import { getCurrentInstance } from 'vue'
const { appContext } = getCurrentInstance()
const { globalProperties } = appContext.config
const myUrl = globalProperties.$globalVar
const router = useRouter()
const md = new MarkdownIt();
md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
    tokens[idx].attrPush(['target', '_blank']);
    return self.renderToken(tokens, idx, options);
};

let socket = io.connect(myUrl);
let lastQuestion;



socket.on('connect', function() {
    console.log("connected！")
});

socket.on('response',function(msg){

    console.log(msg)
    if(msg.question !== lastQuestion)
        return;
    const image = msg.image ? 'data:image/png;base64,' + msg.image : null;
    const reply = markdownToHtml(msg.reply);
    messages.value.push({ side: 'left', content: reply, image });
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

function handleClickChatLog(chat_name){
    console.log(chat_name);
    axios.post(myUrl+'/chatHistory',
        {
            username: localStorage.getItem('inviteCode'),
            time: chat_name,
        })
        .then(response => {
            console.log("get");
            let chat_history = response.data.history;
            for(let i = 0;i < chat_history.length;i++){
                 let chat = chat_history[i];
                 messages.value.push({ side: 'right', content: chat.question });
                 const image = chat.image ? 'data:image/png;base64,' + chat.image : null;
                 const reply = markdownToHtml(chat.response);
                 messages.value.push({ side: 'left', content: reply, image });
            }
            scrollToBottom();


        })
        .catch(error => {
            console.error('Error:', error);

        });
}

function handleBack() {
    router.push('/login');
}

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
        clearTimeout(timerId);
        timerId = setTimeout(myFunction, delay);
        socket.connect();
        // 获取用户名
        let userName = localStorage.getItem('inviteCode')

        //console.log(userName)
        socket.emit('message', {"username": userName,"data": msg});
        //socket.emit('message', {"data": msg});
    } catch (error) {
        console.error(error);
        this.sendMessage();
    }
}

function markdownToHtml(markdownText) {
    return md.render(markdownText);
}

function scrollToBottom() {
    const chat = document.querySelector('.chat');
    chat.scrollTop = chat.scrollHeight;
}

onUpdated(() => {
    console.log("update")
    scrollToBottom();
});

onMounted(()=>{
    console.log("mounted")

    axios.post(myUrl+'/chatHistoryList',
        {
        username: localStorage.getItem('inviteCode'),
        })
        .then(response => {
           console.log("get");
           // let chat_history = response.data.history;
           // for(let i = 0;i < chat_history.length;i++){
           //     let chat = chat_history[i];
           //     messages.value.push({ side: 'right', content: chat.question });
           //     const image = chat.image ? 'data:image/png;base64,' + chat.image : null;
           //     const reply = markdownToHtml(chat.response);
           //     messages.value.push({ side: 'left', content: reply, image });
           // }
           //  scrollToBottom();
            let history_list = response.data.history_list;
            // for (let k = 0;k < 20;k++)
            for(let i = 0;i < history_list.length;i++){
                chatLogs.value.push(history_list[i]);
            }

        })
        .catch(error => {
            console.error('Error:', error);

        });

})

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
.chatpdf{
    display: flex;
    height: 100vh;
    flex-direction: row;
}
.pannel{
    width: 255px;
    background-color: rgb(0, 21, 41);
    height: 100vh;
}
.chatbotTitle {
    font-size: 24px;
    color: #fff;
    text-align: center;
    padding: 20px;
}
.sideList {
    flex-grow: 1;
    overflow-y: scroll;
    margin-bottom: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #f6f8fa;
    height: 50vh;
}
.fileTitle{
    background-color: #6f7d91;
    color: #fff;
    border-radius: 8px;
    padding: 10px;
    margin: 10px;
    font-size: 14px;
    cursor: pointer;
}
.container {
    display: flex;
    flex-direction: column;
    flex: 1;
    margin: 0 auto;
    padding: 20px 10px;
    background-color: #fff;
    background-size: cover;
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

.back-icon-container {
    position: absolute;
    top: 0.7rem;
    left: 0.7rem;
    z-index: 1;

}

.icon {
    width: 1.5rem;
    height: 1.5rem;
    cursor: pointer;
    color: #ffffff;
}

</style>
