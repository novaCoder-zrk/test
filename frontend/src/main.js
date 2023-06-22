import {createApp} from 'vue'
import App from './App.vue'
import Login from '/src/view/Login.vue'
import Chatbot from '/src/view/Chatbot.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import {createRouter, createWebHashHistory} from "vue-router";

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login,
    },
    {
        path: '/chatbot/:username',
        name: 'Chatbot',
        component: Chatbot,
        //props: true,
    },
    {
        path: '/',
        redirect: '/login',
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
