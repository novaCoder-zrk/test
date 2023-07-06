<template>
    <div class="login-container">
        <h1 class="title">Welcome to Chatbot!</h1>
        <div class="login-form">
            <label class="label">Username</label>
            <input  class="input" type="text" placeholder="Enter your username" id="username" v-model="username"/>

            <label class="label">Password</label>
            <input  class="input" type="password" placeholder="Enter your password" id="password" v-model="password"/>
            <span style="margin-top: 3rem;color: gray; ">Don't have an account? <router-link to="/register">sign up</router-link></span>
            <span style="margin-top: 0.5rem;color: gray;">Forgot password? <router-link to="/resetpassword">click here</router-link></span>

            <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
        </div>
        <button class="login-button" @click="handleLogin">Sign In</button>
    </div>
</template>

<script setup>
import {reactive, ref} from 'vue'
import axios from 'axios'
import {useRouter} from 'vue-router'

const router = useRouter()

//const myUrl = "http://localhost:16161";
// const myUrl = "http://54.206.93.57:16161";
import { getCurrentInstance } from 'vue'
const { appContext } = getCurrentInstance()
const { globalProperties } = appContext.config
const myUrl = globalProperties.$globalVar
console.log("my url "+myUrl)
let username = ref("");
let password = ref("");
let errorMessage = ref("");

function handleLogin() {
    errorMessage.value = "";
    // 发送登录请求
    axios.post(myUrl+'/login', { account: username.value, password: password.value })
        .then(response => {
            const { invitecode, token } = response.data;
            if (invitecode === 'default') {
                console.log('Login failed');
                errorMessage.value = "Login failed, please check your username and password.";
            } else {
                localStorage.setItem('token', token);
                localStorage.setItem('inviteCode', invitecode);
                router.push(`/chatbot/${invitecode}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            errorMessage.value = "An error occurred, please try again later.";
        });
}

</script>

<style>
.error {
    color: red;
    margin-top: 1rem;
}

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
    width: 80vw;
    max-width: 400px;
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
    width: 80vw;
    max-width: 400px;
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

@media (max-width: 768px) {
    .title {
        font-size: 1.5rem;
    }

    .login-form {
        padding: 1rem;
    }

    .label {
        font-size: 1rem;
        margin-top: 1rem;
    }

    .login-button {
        font-size: 1rem;
    }
}
</style>
