<template>
    <div>
        <h1>Login Page</h1>
        <div>
            <label for="username">Username:</label>
            <input type="text" id="username" v-model="username"/>
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" v-model="password"/>
        </div>
        <button @click="handleLogin">Login</button>
    </div>
</template>

<script setup>
import {reactive, ref} from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

let username = ref("");
let password = ref("");
function handleLogin(){
    router.push(`/chatbot/`+username.value)
}


</script>