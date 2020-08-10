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
                <b-input v-model="search" id="inline-form-input-search" placeholder="search item to add"></b-input>
                <b-input-group-append>
                  <b-button title="Scan a barcode" v-b-modal.modal-barcode-scanner><i class="fa fa-barcode" aria-hidden="true"></i></b-button>
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

    <b-modal size="lg" id="modal-barcode-scanner" title="Scan a barcode" hide-footer>
      <b-row>
        <b-col align="center">
          <v-quagga class="barcodeScanner" :onDetected="codeScanned" :readerSize="barcodeScanner.readerSize" :readerTypes="barcodeScanner.types"></v-quagga>
        </b-col>
      </b-row>
    </b-modal>
  </div>
</template>

<style lang="scss" src="./App.scss"></style>

<script>
import { mapState } from 'vuex'

export default {
  data() {
    return {
      search: '',
      barcodeScanner: {
        readerSize: {
          width: 640,
          height: 480
        },
        detected: [],
        types: ['ean_reader'],
        scanDone: false
      }
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
      let search = this.search
      this.search = ''
      this.$router.replace({ name: 'SearchNew', query: {q: search} }).catch(() => {})
    },
    openBarcodeScanner () {

    },
    codeScanned (data) {
      console.log('detected barcode', data)
      if (data.codeResult.format === 'ean_13') {
        this.$root.$emit('bv::hide::modal', 'modal-barcode-scanner', '#btnManage')
        this.$router.replace({ name: 'SearchNew', query: { q: data.codeResult.code } }).catch(() => {})
      }
    }
  }
}
</script>