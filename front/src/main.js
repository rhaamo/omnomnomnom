import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import i18n from './i18n'
import Axios from 'axios'
import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue'

Vue.config.productionTip = false

Axios.defaults.baseURL = 'http://192.168.10.167:5000'
Axios.defaults.headers.common['Accept'] = 'application/json'
Axios.defaults.headers.common['Content-Type'] = 'application/json'

Axios.interceptors.request.use(function (config) {
  if (["post", "delete", "patch", "put"].includes(config["method"])) {
    // Set CSRF Token if known
    if (store.state.csrfToken !== '') {
      config.headers["X-CSRF-Token"] = store.state.csrfToken
    }
  }
  if (["post", "delete", "patch", "put", "get"].includes(config["method"])) {
    // Set then Authentication Token if known
    if (store.state.authToken !== '') {
      config.headers["Authentication-Token"] = store.state.authToken
    }
  }
  
  return config;
}, function (error) {
  // Do something with request error
  return Promise.reject(error);
});

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
