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
                    Expiries: <span v-for="(element, index) in item.expiries" :key="index"><span v-if="index != 0">, </span><span :class="expiryVariant(element)">{{ shortDate(element) }}</span></span>
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
                <template v-if="errorSavingSubitem">
                    <b-alert show fade variant="danger">Error while adding a subitem!</b-alert>
                </template>

                <b-form @submit="addNewSubitem">
                    <b-row>
                        <b-col cols="3" offset-md="1">
                            <b-form-group id="add-qty">
                                <label class="sr-only" for="input-add-qty">Qty</label>
                                <b-input size="sm" v-model="newSubitem.qty" type="number" id="input-add-qty" :state="$v.newSubitem.qty.$dirty ? !$v.newSubitem.qty.$error : null"></b-input>
                                <b-form-invalid-feedback id="input-add-qty-feedback">1 minimum</b-form-invalid-feedback>
                            </b-form-group>
                        </b-col>

                        <b-col cols="5">
                            <b-form-group id="add-qty">
                                <label class="sr-only" for="input-add-expiry">Expires</label>
                                <b-input size="sm" v-model="newSubitem.expiry" type="date" id="input-add-expiry"></b-input>
                            </b-form-group>
                        </b-col>

                        <b-col cols="3" align="center">
                            <b-button size="sm" type="submit" variant="primary">add</b-button>
                        </b-col>
                    </b-row>
                </b-form>

                <b-table stripped hover small :items="choosen.item.subitems" :fields="modalManage.fields">
                    <template v-slot:cell(expiry)="data"><span :class="expiryVariant(data.item.expiry)">{{shortDate(data.item.expiry)}}</span></template>
                    <template v-slot:cell(added)="data">{{shortDate(data.item.added)}}</template>
                    <template v-slot:cell(actions)="data">
                        <i class="fa fa-pencil-square-o" aria-hidden="true"></i>
                        &nbsp;
                        <a href="#" @click="deleteSubitem(choosen.item.flake_id, data.item.id, data.item.expiry)"><i class="fa fa-times" aria-hidden="true"></i></a>
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
import { required, minValue } from 'vuelidate/lib/validators'
import { validationMixin } from "vuelidate";

export default {
    props: {
        page: {
            type: Number,
            default: 1
        }
    },
    mixins: [validationMixin],
    validations: {
        newSubitem: {
            qty: { required, minValue }
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
            },
            newSubitem: {
                qty: 1,
                expiry: null
            },
            errorSavingSubitem: false,
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
        daysBetweenDateAndNow (date) {
            let a = Moment(date)
            let b = Moment()
            return a.diff(b, 'days')
        },
        expiryVariant (date) {
            let days = this.daysBetweenDateAndNow(date)+1
            if (days <= 2) {
                return "expiry-danger"
            } else if (days > 2 && days <= 7) {
                return "expiry-warning"
            } else {
                // osef
                return "expiry-normal"
            }
        },
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
        fetchItem: function (flake_id) {
            return Axios.get(`/api/v1/item/${flake_id}`).then(resp => {
                this.choosen.item = resp.data
                this.choosen.loaded = true
            }).catch((error) => {
                console.log('Got an error while trying to load item subitems:', error.request, error.response)
                this.loadingErrors.subitems = true
            })
        },
        openModalManage: function (item) {
            this.fetchItem(item.flake_id).then(() => {
                this.$root.$emit('bv::show::modal', 'modal-manage', '#btnManage')
            })
            .catch(() => {
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
        },
        addNewSubitem: function (event) {
            event.preventDefault()
            this.$v.newSubitem.$touch()

            if (!this.$v.newSubitem.$anyError) {
                let subitemDatas = {
                    qty: this.newSubitem.qty,
                    expiry: this.newSubitem.expiry
                }
                Axios.post(`/api/v1/item/${this.choosen.item.flake_id}/subitem/new`, subitemDatas).then(() => {
                    this.resetSubitemForm()
                    this.errorSavingSubitem = false
                    this.fetchItem(this.choosen.item.flake_id)
                    this.fetchItems(this.current_page)
                })
                .catch((error) => {
                    console.log('Got an error while trying to add a subitem:', error)
                    this.errorSavingSubitem = true
                })
            }
        },
        deleteSubitem: function (flake_id, subitem_id, expiry) {
            this.$bvModal.msgBoxConfirm(`Are you sure you want to delete this subitem expiring on ${this.shortDate(expiry) || 'unknown date'}`, {
                title: 'Deleting subitem',
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
                    Axios.delete(`/api/v1/item/${flake_id}/subitem/${subitem_id}`).then(resp => {
                        if (resp.data === "OK") {
                            // reload item
                            this.fetchItem(flake_id)
                            this.fetchItems(this.current_page)
                        } else {
                            console.log("We didn't got OK while removing the subitem :(", resp.data)
                        }
                    })
                    .catch((error) => {
                        console.log(`Got an error while trying to delete the subitem ${flake_id}/${subitem_id}:`, error)
                    })
                }
            })
            .catch(err => {
                console.log("An error occured for the delete popup:", err)
            })
        },
        resetSubitemForm: function () {
            this.newSubitem.qty = 1
            this.newSubitem.expiry = null
        }
    },
    watch: {
        'page': function (val, ) {
            this.fetchItems(val)
        }
    }

}
</script>
