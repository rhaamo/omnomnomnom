<template>
  <div id="app">

    <b-navbar toggleable="lg" type="dark" variant="info">
      <b-navbar-brand href="/">OmNomNomNom</b-navbar-brand>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav>

          <b-nav-item :to="{name: 'Home'}">Home</b-nav-item>

          <template v-if="loggedIn">
           <b-nav-item><a href="#logout" @click.prevent="logout">Logout</a></b-nav-item>
          </template>

          <template v-else>
            <b-nav-item :to="{name: 'Login'}">Login</b-nav-item>
          </template>

          <b-nav-item :to="{name: 'About'}">About</b-nav-item>

        </b-navbar-nav>

        <b-navbar-nav class="ml-auto" v-if="loggedIn">
          <b-nav-form>
            <b-form @submit="doSearch">
              <b-input-group class="mb-2 mr-sm-2 mb-sm-0">
                <b-input v-model="search" id="inline-form-input-search" placeholder="search item"></b-input>
                <b-input-group-append>
                  <b-button title="Scan a barcode"><i class="fa fa-barcode" aria-hidden="true"></i></b-button>
                </b-input-group-append>
              </b-input-group>
            </b-form>
          </b-nav-form>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>

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
  data() {
    return {
      search: ''
    }
  },
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
    },
    doSearch (event) {
      event.preventDefault()
      this.$router.replace({ name: 'SearchNew', query: {q: this.search} })
    }
  }
}
</script>