<template>
    <div class="login-container">
        <h1 class="title">Welcome!</h1>
        <div class="login-form">
            <label class="label">Username</label>
            <input  class="input" type="text" placeholder="Enter your username" id="username" v-model="username"/>

            <label class="label">Password</label>
            <input  class="input" type="password" placeholder="Enter your password" id="password" v-model="password"/>
            <span style="margin-top: 3rem;color: gray; ">Don't have an account? <router-link to="/register">sign up</router-link></span>
            <span style="margin-top: 0.5rem;color: gray;">Forgot password? <router-link to="/resetpassword">click here</router-link></span>
        </div>
        <button class="login-button" @click="handleLogin">Sign In</button>
    </div>
</template>

<script setup>
import {reactive, ref} from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

let username = ref("");
let password = ref("");
function handleLogin(){
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

.login-form {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 400px;
    height: 400px;
    background-color: #fff;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.label {
    font-size: 1.2rem;
    font-weight: bold;
    margin-top: 2rem;
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
</style>