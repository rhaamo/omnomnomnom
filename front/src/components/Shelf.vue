<template>
  <div class="shelf">
    <h1>shelf ({{count}} items)</h1>

    <template v-if="errorFetching">
        <b-alert show fade variant="danger">Error while fetching shelf!</b-alert>
    </template>

    <b-card-group deck>
        <div class="result" v-for="item in items" :key="item.flake_id">
            <b-card
                :title="item.openfoodfacts_product.product_name"
                :img-src="item.openfoodfacts_product.image_front_small_url"
                :img-alt="item.openfoodfacts_product.product_name"
                tag="article"
                style="max-width: 15rem;"
                class="mb-2"
            >
                <b-card-text>
                    Quantities: {{item.qty}}<br>
                    Expiries: {{ item.expiries.join(', ') }}
                </b-card-text>

                <b-button v-b-modal.modal-add variant="primary" ref="btnAdd" @click="openModalAdd(item)" title="Add to shelf"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></b-button>&nbsp;
                <b-button variant="info"><a :href="openFoodFactsUrl(item._id)" target="_blank">OpenFoodFacts</a></b-button>
            </b-card>
        </div>
    </b-card-group>
  </div>
</template>

<script>
import Axios from 'axios'

export default {
    data() {
        return {
            items: [],
            page: 0,
            page_size: 0,
            count: 0,
            total_pages: 0,
            errorFetching: null
        }
    },
    computed: {
    },
    mounted: function () {
        this.fetchItems()
    },
    methods: {
        openFoodFactsUrl (id) { return `https://world.openfoodfacts.org/product/${id}` },
        fetchItems: function () {
            Axios.get('/api/v1/items').then(resp => {
                this.items = resp.data.items
                this.page = resp.data.page
                this.page_size = resp.data.page_size
                this.count = resp.data.count
                this.total_pages = resp.data.total_pages
                this.errorFetching = false
            })
            .catch((error) => {
                console.log('Got an error while trying to save item:', error.request, error.response)
                this.errorFetching = true
            })
        }
    }

}
</script>
