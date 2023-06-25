<script setup>
import {reactive, ref} from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

let username = ref("");
let password = ref("");
let email = ref("");
function handleSignUp(){
    if( username.value !== "")
        router.push(`/login`)
}


</script>

<template>
    <div class="login-container">
        <h1 class="title">Sign Up!</h1>
        <div class="register-form">
            <label class="label">Username</label>
            <input  class="input" type="text" placeholder="Enter your username" id="username" v-model="username"/>
            <label class="label">Email</label>
            <input  class="input" type="text" placeholder="Enter your email" id="email" v-model="email"/>
            <label class="label">Password</label>
            <input  class="input" type="password" placeholder="Enter your password" id="password" v-model="password"/>
            <input  class="input" type="password" placeholder="Repeat your password" id="password" v-model="password"/>
        </div>
        <button class="login-button" @click="handleSignUp">Sign Up</button>
    </div>
</template>

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
    height: 400px;
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
</style>