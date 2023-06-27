<template>
    <div class="login-container">
        <h1 class="title">Reset Password!</h1>
        <div class="reset-form">
            <label class="label">Username</label>
            <input  class="input" type="text" placeholder="Enter your username" id="username" v-model="username"/>
            <label class="label">Email</label>
            <div class="email-form">
                <input  class="email-input" type="text" placeholder="Enter your email" id="email" v-model="email"/>
                <button class="send-email-button" @click="handleSend">Send Email</button>
            </div>
            <input  class="input" type="text" placeholder="Enter verify code" id="verify" v-model="verifycode"/>
            <label class="label">Password</label>
            <input  class="input" type="password" placeholder="Enter your new password" id="password" v-model="password"/>
            <input  class="input" type="password" placeholder="Repeat your new password" id="password" v-model="password"/>
        </div>
        <button class="login-button" @click="handleReset">Reset Password</button>
    </div>
</template>

<script setup>
import {reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
const router = useRouter()

let username = ref("");
let password = ref("");
let verifycode = ref("");
function handleSend(){
    if( username.value !== "")
        router.push(`/chatbot/`+username.value)
}

function handleReset(){
    if( username.value !== "")
        router.push(`/chatbot/`+username.value)
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
</style>