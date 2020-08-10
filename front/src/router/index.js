import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Login from '../views/Login.vue'
import SearchNew from '../views/SearchNew.vue'
import store from '../store'

Vue.use(VueRouter)

const validateAuthenticatedRoute = (to, from, next) => {
  if (store.state.loggedIn) {
    next()
  } else {
    next('/auth/login')
  }
}

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/about', name: 'About', component: About },
  { path: '/auth/login', name: 'Login', component: Login },
  { path: '/items/new/search', name: 'SearchNew', component: SearchNew, props: route => ({ query: route.query.q }), beforeEnter: validateAuthenticatedRoute }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
