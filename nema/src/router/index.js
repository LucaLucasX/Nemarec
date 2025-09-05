// router/index.js
import VueRouter, {createRouter, createWebHistory} from 'vue-router'
import HelloWorld from '../components/HelloWorld.vue'
import ChatView from '../components/ChatView.vue'
import Vue from "vue";
import F from "../components/F.vue"; // 假设你的HelloWorld组件在这个路径

Vue.use(VueRouter)
const routes = [
  {
    path: '/picRec',
    name: 'HelloWorld',
    component: HelloWorld
  },
  {
    path:'/',
    name:'Home',
    component: F
  },
        { path: '/chat',
          name:'Chat',
        component: ChatView },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
});
export default router
