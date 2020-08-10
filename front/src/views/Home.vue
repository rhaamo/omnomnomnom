<template>
  <div class="home">
    <Shelf :page="page" v-if="loggedIn"/>
    <span v-else>Please log in to access shelf.</span>
  </div>
</template>

<script>
import Shelf from '@/components/Shelf.vue'
import { mapState } from 'vuex'

export default {
  props: ['page'],
  name: 'Home',
  components: {
    Shelf
  },
  computed: {
    ...mapState(['loggedIn'])
  }
}
</script>
