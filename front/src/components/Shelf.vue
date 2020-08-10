<template>
  <div class="shelf">
    <h1>shelf ({{count}} items)</h1>

    <template v-if="errorFetching">
        <b-alert show fade variant="danger">Error while fetching shelf!</b-alert>
    </template>

    <b-card-group deck>
        <div class="result" v-for="item in items" :key="item.flake_id">
            <b-card
                :title="decode(item.openfoodfacts_product.product_name)"
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

                <b-button v-b-modal.modal-edit variant="primary" ref="btnAdd" @click="openModalManage(item)" title="Manage item"><i class="fa fa-cutlery" aria-hidden="true"></i></b-button>&nbsp;
                <b-button variant="info"><a :href="openFoodFactsUrl(item._id)" target="_blank">OpenFoodFacts</a></b-button>
            </b-card>
        </div>
    </b-card-group>

    <div class="overflow-auto">
        <b-pagination-nav :link-gen="linkGen" :number-of-pages="total_pages" v-model="current_page" no-page-detect use-router></b-pagination-nav>
    </div>
  </div>
</template>

<script>
import Axios from 'axios'

export default {
    props: {
        page: {
            type: Number,
            default: 1
        }
    },
    data() {
        return {
            items: [],
            current_page: 1,
            page_size: 0,
            count: 0,
            total_pages: 1,
            errorFetching: null
        }
    },
    computed: {
    },
    mounted: function () {
        this.fetchItems(1)
    },
    methods: {
        decode (str) {
            let parser = new DOMParser();
            let dom = parser.parseFromString(str, 'text/html')
            return dom.body.textContent
        },
        openFoodFactsUrl (id) { return `https://world.openfoodfacts.org/product/${id}` },
        linkGen (pageNum) { return { path: `/?page=${pageNum}` } },
        fetchItems: function (page) {
            Axios.get('/api/v1/items', { params: { page: page } }).then(resp => {
                this.items = resp.data.items
                this.current_page = resp.data.page
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
    },
    watch: {
        'page': function (val, ) {
            this.fetchItems(val)
        }
    }

}
</script>
