<template>
  <div id="app">
<router-view></router-view>
<!--    <img alt="Vue logo" src="./assets/1_top.jpg">-->
<!--<HelloWorld/>-->
<!--    <F/>-->

  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'
import  ChatView from './components/ChatView.vue'
import F from "./components/F.vue";

export default {
  name: 'App',
  components: {
      HelloWorld,
    F,
    ChatView
  }
}
</script>

<style>
body{
    margin:0;
    padding:0;
    border:0
  }
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0px;
}
</style>
