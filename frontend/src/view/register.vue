<template>
    <div class="login-container">
        <h1 class="title">Sign Up!</h1>
        <div class="register-form">
            <label class="label">Username</label>
            <input class="input" type="text" placeholder="Enter your username" id="username" v-model="username"/>
            <label class="label">Email</label>
            <input class="input" type="text" placeholder="Enter your email" id="email" v-model="email"/>
            <label class="label">Password</label>
            <input class="input" type="password" placeholder="Enter your password" id="password" v-model="password"/>
            <input class="input" type="password" placeholder="Repeat your password" id="password" v-model="password"/>
            <label class="label">Invite Code</label>
            <input class="input" type="text" placeholder="Enter your invite code" id="invitecode" v-model="invitecode" />
        </div>
        <button class="login-button" @click="handleRegister">Sign Up</button>
        <button class="login-button" @click="handleBackToLogin">Back to Login</button>
        <p class="success-message" v-if="registrationSuccess">Succeed!</p>
        <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const myUrl = "http://localhost:16161";

let invitecode = ref("");
let username = ref("");
let password = ref("");
let email = ref("");
let errorMessage = ref("");
let registrationSuccess = ref(false);

function handleRegister() {
    axios.post(myUrl+'/register', {
        invitecode: invitecode.value,
        account: username.value,
        password: password.value,
        email: email.value
    })
        .then(response => {
            const { message } = response.data;
            if (message === 'Registration successful') {
                registrationSuccess.value = true;
            } else {
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
</style>