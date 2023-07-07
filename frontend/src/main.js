import { createApp } from 'vue'
import axios from 'axios'
import App from './App.vue'
import Login from '/src/view/Login.vue'
import Chatbot from '/src/view/Chatbot.vue'
import Register from '/src/view/register.vue'
import Resetpassword from '/src/view/Resetpassword.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createRouter, createWebHashHistory } from "vue-router";

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login,
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
    },
    {
        path: '/resetpassword',
        name: 'Resetpassword',
        component: Resetpassword,
    },
    {
        path: '/chatbot/:username',
        name: 'Chatbot',
        component: Chatbot,
        meta: { requiresAuth: true }
    },
    {
        path: '/:pathMatch(.*)*',
        redirect: '/login',
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

router.beforeEach(async (to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const isAuthenticated = await checkIfUserIsAuthenticated();
    const validInviteCode = checkInviteCode(to.params.username);

    if (requiresAuth && !isAuthenticated) {
        next('/login');
    } else if (requiresAuth && !validInviteCode) {
        next('/login');
    } else {
        next();
    }
});

function checkInviteCode(inviteCode) {
    const storedInviteCode = localStorage.getItem('inviteCode');
    return inviteCode === storedInviteCode;
}

async function checkIfUserIsAuthenticated() {
    const token = localStorage.getItem('token');

    if(!token) {
        return false;
    }

    try {
        const response = await axios.post(myUrl+'/verifyToken', {}, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return response.data.isValid;
    } catch (error) {
        console.error('Error verifying token:', error);
        return false;
    }
}

// const myUrl = "http://localhost:16161";
const myUrl = "http://54.206.93.57:16161";

const app = createApp(App)
app.config.globalProperties.$globalVar = myUrl;
app.use(ElementPlus)
app.use(router)
app.mount('#app')
