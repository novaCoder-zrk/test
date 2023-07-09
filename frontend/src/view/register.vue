<template>
    <div class="login-container">
        <h1 class="title">Sign Up!</h1>
        <div class="register-form">
            <img class="icon"  @click="handleBackToLogin"  src="../assets/back.svg"  alt="go back"/>
            <label class="label">Username</label>
            <input class="input" type="text" placeholder="Enter your username" id="username" v-model="username"/>
            <span class="illegalText">{{accountErrorText}}</span>
            <label class="label">Email</label>
            <div class="email-form">
                <input class="email-input" type="text" placeholder="Enter your email" id="email" v-model="email"/>
                <button class="send-email-button" @click="handleSend" id="send_email">{{sendButton}}</button>
            </div>
            <input  class="input" type="text" placeholder="Enter verify code" id="email" v-model="verifyCode"/>
            <span class="illegalText">{{emailErrorText}}</span>
            <label class="label">Password</label>
            <input class="input" type="password" placeholder="Enter your password" id="password" v-model="password"/>
            <input class="input" type="password" placeholder="Repeat your password" id="repeatPassword" v-model="repeatPassword"/>
            <span class="illegalText">{{ passwordMismatch }}</span>
            <label class="label">Invite Code</label>
            <input class="input" type="text" placeholder="Enter your invite code" id="invitecode" v-model="invitecode" />
        </div>
        <button class="login-button" @click="handleRegister">Sign Up</button>
        <p class="success-message" v-if="registrationSuccess">Succeed!</p>
        <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

import { getCurrentInstance } from 'vue'
const { appContext } = getCurrentInstance()
const { globalProperties } = appContext.config
const myUrl = globalProperties.$globalVar

const router = useRouter()

let invitecode = ref("");
let username = ref("");
let password = ref("");
let repeatPassword = ref("");
let email = ref("");
let errorMessage = ref("");
let passwordMismatch = ref("");
let registrationSuccess = ref(false);
let sendButton = ref("Send Email")
let verifyCode = ref("");
let timerId;
let countDown = 0;
let sendAble = true;
let accountErrorText = ref("");
let emailErrorText = ref("");

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
        const send_email = document.getElementById('send_email');
        send_email.style.backgroundColor = '#4f46e5';
        clearInterval(timerId);
    }
}

function handleSend(){
    registrationSuccess.value = false;
    errorMessage.value = "";
    accountErrorText.value = "";
    emailErrorText.value = "";
    if(!sendAble)
        return;


    sendAble = false;
    sendButton.value="60 s";
    const send_email = document.getElementById('send_email');
    send_email.style.backgroundColor = 'grey';
    clearInterval(timerId);
    countDown = 60;
    timerId = setInterval(myFunction, 1000);
    if( username.value !== ""){
        axios.post(myUrl+'/sendVerifyCodeByEmail', {
            account: username.value,
            email: email.value,
        })
            .then(response => {
                const message = response.data.message;
                console.log(message)
                if (message === 'success') {
                    console.log("have send!")
                }
                else {
                    const account_msg = response.data.account_msg;
                    const email_msg = response.data.email_msg;
                    if (account_msg !== "")
                        accountErrorText.value = account_msg;
                    if (email_msg !== "")
                        emailErrorText.value = email_msg;
                    sendButton.value="Send Email";
                    sendAble = true;
                    send_email.style.backgroundColor = '#4f46e5';
                    clearInterval(timerId);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });

    }

}

function checkPasswordMatch() {
    if (password.value !== repeatPassword.value) {
        passwordMismatch.value = "Passwords do not match!";
    } else {
        passwordMismatch.value = "";
    }
}

function handleRegister() {
    checkPasswordMatch();
    if (passwordMismatch.value) return;

    errorMessage.value = "";
    emailErrorText.value = "";
    registrationSuccess.value = false;
    passwordMismatch.value = "";

    axios.post(myUrl+'/register', {
        invitecode: invitecode.value,
        account: username.value,
        password: password.value,
        email: email.value,
        verify_code: verifyCode.value,
    })
        .then(response => {
            const message  = response.data.message;
            if (message === 'Registration successful') {
                clearInterval(timerId);
                registrationSuccess.value = true;
                alert('Registration successful!');
                router.push('/login');
            } else {
                const email_msg = response.data.email_msg;
                if(email_msg !== ''){
                    emailErrorText.value = email_msg;
                }
                errorMessage.value = message;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            errorMessage.value = "An error occurred, please try again later.";
        });
}

function handleBackToLogin() {
    router.push('/login');
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

.register-form {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 400px;
    max-width: 500px;
    height: 625px;
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
    border: none;
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

.error-message {
    color: red;
    margin-top: 1rem;
}

.success-message {
    color: green;
    margin-top: 1rem;
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
.illegalText {
//position: absolute;
    color: red;
    font-size: 12px;
}

@media (max-width: 768px) {
    .login-container {
        padding: 1rem;
    }

    .register-form {
        width: 100%;
        padding: 1rem;
        box-sizing: border-box;
        max-width: 500px;
    }

    .login-button {
        width: 100%;
    }
}

@media (max-width: 500px) {
    .title {
        font-size: 1.5rem;
    }

    .label {
        font-size: 1rem;
    }

    .input, .email-input {
        font-size: 0.9rem;
    }

    .login-button {
        font-size: 1rem;
    }
}
</style>
