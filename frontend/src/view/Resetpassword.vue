<template>
    <div class="login-container">

        <h1 class="title">Reset Password!</h1>
        <div class="reset-form">
            <img class="icon"  @click="handleBackToLogin"  src="../assets/back.svg" />
            <label class="label">Username</label>
            <input  class="input" type="text" placeholder="Enter your username" id="username" v-model="username"/>
            <span class="illegalText">{{accountErrorText}}</span>
            <label class="label">Verify Code</label>
            <div class="email-form">
                <input  class="email-input" type="text" placeholder="Enter verify code" id="email" v-model="verifyCode"/>
                <button class="send-email-button" @click="handleSend">{{sendButton}}</button>
            </div>
            <span class="illegalText">{{codeErrorText}}</span>
            <label class="label">Password</label>
            <input  class="input" type="password" placeholder="Enter your new password"  v-model="password1"/>
            <input  class="input" type="password" placeholder="Repeat your new password"  v-model="password2"/>
            <span class="illegalText">{{passwordErrorText}}</span>
        </div>
        <button class="login-button" @click="handleReset">Reset Password</button>

    </div>
</template>

<script setup>
import {reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
const router = useRouter()
import axios from 'axios'

let username = ref("");
let password1 = ref("");
let password2 = ref("");
let verifyCode = ref("");
let passwordErrorText = ref("");
let codeErrorText = ref("")
let accountErrorText = ref("");
let sendAble = true;
let sendButton = ref("Send Email");
let timerId;
let countDown = 0;
const myUrl = "http://localhost:16161";


function handleBackToLogin() {
    router.push('/login');
}

function myFunction() {
    console.log("定时器到期，执行函数");
    if(countDown > 0){
        sendAble = false;
        countDown = countDown -1;
        sendButton.value = countDown.toString() + " s";
        console.log("interval"+ countDown);
    }else{
        sendAble = true;
        sendButton.value="Send Email";
        clearInterval(timerId);
    }
}
function handleSend(){
    if(!sendAble)
        return;

    accountErrorText.value = "";
    sendAble = false;
    sendButton.value="60 s";
    clearInterval(timerId);
    countDown = 60;
    timerId = setInterval(myFunction, 1000);
    if( username.value !== ""){
        axios.post(myUrl+'/sendVerifyCode', {
            account: username.value,
        })
            .then(response => {
                const message = response.data.message;
                if (message === 'success') {
                    console.log("have send!")
                }
                else {
                    sendButton.value="Send Email";
                    accountErrorText.value = "no account";
                    clearInterval(timerId);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });

    }

}

function handleReset(){

    passwordErrorText.value = "";
    codeErrorText.value = "";

    if(password1.value !== password2.value) {
        passwordErrorText.value = "pass world not same";
        console.log("密码不一致")
        return;
    }else{
        axios.post(myUrl+'/resetPassword', {
            account: username.value,
            verify_code: verifyCode.value,
            password: password1.value,
        })
            .then(response => {
                const message = response.data.message;
                if (message === 'success'){
                    alert("Reset password successfully!")
                    console.log("reset success")
                }
                else{
                    codeErrorText.value = "wrong verify code";
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

}
</script>

<style>
.login-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background-color: #f5f5f5;
}

.title {
    font-size: 2rem;
    font-weight: bold;
    color: #2196f3;
    margin-bottom: 2rem;
}
.illegalText {

    //position: absolute;
    color: red;
}
.reset-form {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 400px;
    height: 500px;
    background-color: #fff;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    position: relative;
}

.label {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #2196f3;
}

.input {
    width: 100%;
    padding: 0.5rem;
    margin-bottom: 1rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-button {
    width: 400px;
    padding: 0.5rem;
    margin-top: 1rem;
    border: none;
    border-radius: 4px;
    background-color: #2196f3;
    color: #fff;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-button:hover {
    background-color: #1976d2;
}

.email-form {
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
}

.email-input {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-right: 0.5rem;
    margin-bottom: 1rem;
    flex: 1;
}
.send-email-button {
    background-color: #4f46e5;
    color: #fff;
    height: 2rem;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    border: none;
    cursor: pointer;
    margin-bottom: 1rem;
}

.icon{
    position: absolute; /* 设置绝对定位 */
    top: 15px; /* 将 SVG 图像放在表单的左上角 */
    left: 15px;
    width: 25px;
    height: 25px;
    fill: #333;
}
</style>