import Vue from 'vue'
import App from './App.vue'
import {Upload,Loading} from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css';
import router from "./router";

Vue.config.productionTip = false
Vue.use(Upload)
Vue.use(Loading)

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
