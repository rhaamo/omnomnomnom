<template>
  <div class="shelf">
    <h1>shelf ({{count}} items)</h1>

    <template v-if="loadingErrors.item">
        <b-alert show fade variant="danger">Error while fetching shelf!</b-alert>
    </template>
    <template v-if="loadingErrors.subitems">
        <b-alert show fade variant="danger">Error while fetching item datas!</b-alert>
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
                    Expiries: {{ item.expiries.join(', ') || 'unknown' }}
                </b-card-text>

                <b-button v-b-modal.modal-manage variant="primary" ref="btnAdd" @click="openModalManage(item)" title="Manage item"><i class="fa fa-cutlery" aria-hidden="true"></i></b-button>&nbsp;
                <b-button variant="info"><a :href="openFoodFactsUrl(item.openfoodfacts_product._id)" target="_blank">OpenFoodFacts</a></b-button>
            </b-card>
        </div>
    </b-card-group>

    <div class="overflow-auto">
        <b-pagination-nav :link-gen="linkGen" :number-of-pages="total_pages" v-model="current_page" no-page-detect use-router></b-pagination-nav>
    </div>

    <b-modal size="lg" id="modal-manage" @cancel="cancelItem" @close="cancelItem" @hidden="cancelItem" ref="modal-add">
        <template v-if="choosen.loaded" v-slot:modal-header="{ close }">
            <h5>
                <a :href="openFoodFactsUrl(choosen.item.openfoodfacts_product._id)"><i class="fa fa-external-link" aria-hidden="true" title="View on OpenFoodFacts"></i></a>&nbsp;
                {{modalTitle}}
            </h5>
            <a href="#" @click.prevent="close()"><i class="fa fa-times" aria-hidden="true"></i></a>
        </template>

        <b-row v-if="choosen.loaded">
            <b-col cols="6">
                <b-row>
                    <b-col>
                        <b-row>
                            <b-col cols="6"><img :src="choosen.item.openfoodfacts_product.image_front_small_url"></b-col>
                            <b-col cols="6"><img :src="choosen.item.openfoodfacts_product.image_ingredients_small_url"></b-col>
                        </b-row>
                        
                        <b-row>
                            <b-col v-html="this.choosen.item.openfoodfacts_product.ingredients_text_with_allergens"></b-col>
                        </b-row>
                    </b-col>
                </b-row>
            </b-col>
            <b-col cols="6">
                <b-table stripped hover small :items="choosen.item.subitems" :fields="modalManage.fields">
                    <template v-slot:cell(expiry)="data">{{shortDate(data.item.expiry)}}</template>
                    <template v-slot:cell(added)="data">{{shortDate(data.item.added)}}</template>
                    <template v-slot:cell(actions)>
                        <i class="fa fa-pencil-square-o" aria-hidden="true"></i>
                        &nbsp;
                        <i class="fa fa-times" aria-hidden="true"></i>
                    </template>
                </b-table>
            </b-col>
        </b-row>

        <template v-slot:modal-footer="{ cancel }">
            <b-button size="sm" variant="danger" @click="deleteItem(choosen.item.flake_id, choosen.item.openfoodfacts_product.product_name)">
                Delete
            </b-button>
            <b-button size="sm" variant="success" @click="cancel">
                Close
            </b-button>
        </template>
    </b-modal>

  </div>
</template>

<script>
import Axios from 'axios'
import Moment from 'moment'
// TODO: expires cell variant warning < 1w, danger < 1d

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
            choosen: {
                loaded: false,
                item: {},
            },
            loadingErrors: {
                item: false,
                subitems: false
            },
            modalManage: {
                fields: [
                    { key: 'expiry', label: 'Expires', sortable: true },
                    { key: 'qty', label: 'Qty', sortable: true },
                    { key: 'added', label: 'Added on' },
                    { key: 'actions', label: '-' }
                ]
            }
        }
    },
    computed: {
        modalTitle () { return this.choosen.loaded ? `${this.decode(this.choosen.item.openfoodfacts_product.product_name)} (${this.choosen.item.openfoodfacts_product.code})` : '' },
    },
    mounted: function () {
        this.fetchItems(1)
    },
    methods: {
        shortDate (date) { return date === null ? '' : Moment(date).locale('en').format('ddd D/M/YY') },
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
                this.loadingErrors.item = true
            })
        },
        openModalManage: function (item) {
            Axios.get(`/api/v1/item/${item.flake_id}`).then(resp => {
                this.choosen.item = resp.data
                this.choosen.loaded = true
                this.$root.$emit('bv::show::modal', 'modal-manage', '#btnManage')
            }).catch((error) => {
                console.log('Got an error while trying to load item subitems:', error.request, error.response)
                this.loadingErrors.subitems = true
                this.$root.$emit('bv::hide::modal', 'modal-manage', '#btnManage')
            })
        },
        cancelItem: function () {
            this.choosen.item = {}
            this.choosen.loaded = false
        },
        deleteItem: function (flake_id, product_name) {
            this.$bvModal.msgBoxConfirm(`Are you sure you want to delete: ${this.decode(product_name)}`, {
                title: 'Deleting item',
                size: 'sm',
                buttonSize: 'sm',
                okVariant: 'danger',
                okTitle: 'yes',
                cancelTitle: 'no',
                footerClass: 'p-2',
                hideHeaderClose: false,
                centered: true
            })
            .then(value => {
                    if (value === true) {
                        Axios.delete(`/api/v1/item/${flake_id}`).then(resp => {
                            if (resp.data === "OK") {
                                // reload shelf
                                this.fetchItems(this.current_page)
                                this.cancelItem()
                                this.$root.$emit('bv::hide::modal', 'modal-manage', '#btnManage')
                            } else {
                                console.log("We didn't got OK while removing the item :(", resp.data)
                            }
                        })
                        .catch((error) => {
                            console.log(`Got an error while trying to delete the item ${flake_id}:`, error)
                        })
                    }
            })
            .catch(err => {
                console.log("An error occured for the delete popup:", err)
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
