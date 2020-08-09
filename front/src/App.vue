<template>
  <div id="app">
    <div id="nav">
      <router-link :to="{name: 'Home'}">Home</router-link> |

      <template v-if="loggedIn">
        <a href="#" @click.prevent="logout">Logout</a> |
      </template>
      <template v-else>
        <router-link :to="{name: 'Login'}">Login</router-link> |
      </template>

      <router-link :to="{name: 'About'}">About</router-link>
    </div>

    <b-container>
      <router-view/>
    </b-container>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>

<script>
import { mapState } from 'vuex'

export default {
  mounted: function () {
    this.$store.dispatch('fetchCsrfToken')
  },
  computed: {
    ...mapState(['loggedIn'])
  },
  methods: {
    logout () {
      this.$store.dispatch('logout')
      this.$router.replace({ name: 'Home' })
    }
  }
}
</script>