<template>
  <div class="home">
    <Shelf :page="page" :view="view" v-if="loggedIn"/>

    <div align="center" v-else>Please log in to access shelf.</div>
  </div>
</template>

<script>
import Shelf from '@/components/Shelf.vue'
import { mapState } from 'vuex'

export default {
  props: ['page', 'view'],
  name: 'Home',
  components: {
    Shelf
  },
  computed: {
    ...mapState(['loggedIn'])
  }
}
</script>
