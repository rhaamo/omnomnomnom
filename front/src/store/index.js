import Vue from 'vue'
import Vuex from 'vuex'
import Axios from 'axios'
import createPersistedState from "vuex-persistedstate";

Vue.use(Vuex)

export default new Vuex.Store({
  plugins: [createPersistedState()],
  state: {
    csrfToken: '',
    loggedIn: false
  },
  mutations: {
    setCsrfToken (state, token) {
      state.csrfToken = token
    },
    setLoggedIn (state, loggedIn) {
      state.loggedIn = loggedIn
    }
  },
  actions: {
    fetchCsrfToken (ctx) {
      Axios.get('/api/auth/login', { data: null }).then(function (resp) {
        let token = resp.data['response']['csrf_token']
        ctx.commit('setCsrfToken', token)
      })
    },
    logout (ctx) {
      Axios.post('/api/auth/logout').then(() => {
        ctx.commit('setLoggedIn', false)
      })
    }
  },
  modules: {
  },
  getters: {
    getCsrfToken: state => { return state.csrfToken }
  }
})
