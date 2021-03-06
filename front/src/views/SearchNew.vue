<template>
  <div class="search">
    <h1>Searching for <i>{{ query }}</i></h1>

    <template v-if="warn">
        <b-alert show variant="warning">Too many items returned, only the first {{page_size}} results are shown.</b-alert>
    </template>

    <div class="results" v-if="count === 0 && page_size === 0">
        Search in progress.
    </div>
    <div class="results" v-if="count === 0 && page_size > 0">
        No results.
    </div>
    <div class="results" v-else>

        <b-card-group deck>
            <div class="result" v-for="item in results" :key="item._id">
                <b-card
                    :title="decode(item.product_name)"
                    :img-src="item.image_front_small_url"
                    :img-alt="item.product_name"
                    tag="article"
                    style="max-width: 15rem;"
                    class="mb-2"
                >
                    <b-card-text>
                        {{ decode(item.ingredients_text) }}
                    </b-card-text>

                    <b-row class="justify-content-md-center">
                        <b-col align="center"><b-button v-b-modal.modal-add variant="primary" ref="btnAdd" @click="openModalAdd(item)" title="Add to shelf"><i class="fa fa-plus-square-o" aria-hidden="true"></i></b-button></b-col>
                        <b-col align="center"><a :href="openFoodFactsUrl(item._id)" target="_blank"><b-button variant="info"><i class="fa fa-external-link" aria-hidden="true"></i></b-button></a></b-col>
                    </b-row>
                </b-card>
            </div>
        </b-card-group>
    </div>

    <b-modal id="modal-add" :title="modalTitle" @ok="saveItem" @cancel="cancelItem" ref="modal-add" footer-class="custom-footer-modal">
            <template v-if="errorSaving">
                <b-alert show fade variant="danger">Error while saving item!</b-alert>
            </template>
            <b-form>
                <b-row>
                    <b-col cols="6">
                        <b-form-group id="add-qty" label="Qty" label-for="input-add-qty">
                            <b-input-group>
                                <template v-slot:prepend>
                                    <b-button @click.prevent="qtyMinus" variant="outline-info">-</b-button>
                                </template>
                                <b-input v-model="addItem.qty" type="number" id="input-add-qty" :state="$v.addItem.qty.$dirty ? !$v.addItem.qty.$error : null"></b-input>
                                <template v-slot:append>
                                    <b-button @click.prevent="qtyPlus" variant="outline-info">+</b-button>
                                </template>
                            </b-input-group>

                            <b-form-invalid-feedback id="input-add-qty-feedback">1 minimum</b-form-invalid-feedback>
                        </b-form-group>
                    </b-col>

                    <b-col cols="6">
                        <b-form-group id="add-qty" label="Expires" label-for="input-add-expiry">
                            <b-input v-model="addItem.expiry" type="date" id="input-add-expiry"></b-input>
                        </b-form-group>
                    </b-col>
                </b-row>
            </b-form>

            <template v-slot:modal-footer="{ cancel, ok }">
                <b-row class="justify-content-md-center">
                    <b-col align="center" cols="5"><b-button size="sm" variant="secondary" @click="cancel">Cancel</b-button></b-col>
                    <b-col align="center" cols="5"><b-button size="sm" variant="primary" @click="ok">OK</b-button></b-col>
                </b-row>
            </template>
    </b-modal>

  </div>
</template>

<script>
import { Ean13Utils } from 'ean13-lib'
import Axios from 'axios'
import { required, minValue } from 'vuelidate/lib/validators'
import { validationMixin } from "vuelidate";

export default {
    props: ['query'],
    mixins: [validationMixin],
    data() {
        return {
            results: '',
            count: 0,
            page_size: 0,
            choosen: {},
            warn: false,
            addItem: {
                qty: 1,
                expiry: null
            },
            errorSaving: false
        }
    },
    validations: {
        addItem: {
            qty: { required, minValue }
        }
    },
    computed: {
        isBarcode () { return Ean13Utils.validate(this.query) },
        modalTitle () { return `Add '${this.choosen.product_name}' to shelf` }
    },
    mounted: function () {
        this.fetchResults()
    },
    methods: {
        decode (str) {
            let parser = new DOMParser();
            let dom = parser.parseFromString(str, 'text/html')
            return dom.body.textContent
        },
        openFoodFactsUrl (id) { return `https://world.openfoodfacts.org/product/${id}` },
        fetchResults: function () {
            Axios.get('/api/v1/items/new/search', {params: {q: this.query}}).then(resp => {
                this.count = resp.data.count
                this.page_size = resp.data.page_size
                this.results = resp.data.results
                this.warn = this.count > this.page_size
            })
            .catch((error) => {
                console.log('Got an error while trying to fetch item:', error)
                this.$bvToast.toast(`Cannot fetch search items.`, {title: 'Error', variant: 'danger', solid: true, autoHideDelay: 4000, appendToast: false})
            })
        },
        cancelItem: function () {
            this.choosen = {}
            this.addItem.qty = 1
            this.addItem.expiry = null
            this.$nextTick(() => { this.$v.$reset(); })
        },
        openModalAdd: function (item) {
            this.choosen = item
            this.$root.$emit('bv::show::modal', 'modal-add', '#btnAdd')
        },
        saveItem: function (event) {
            event.preventDefault()
            this.$v.addItem.$touch();

            if (!this.$v.addItem.$anyError) {
                let itemDatas = {
                    openFoodFactsId: this.choosen._id,
                    qty: this.addItem.qty,
                    expiry: this.addItem.expiry
                }
                Axios.post("/api/v1/items/new", itemDatas, {withCredentials: true}).then(() => {
                    this.errorSaving = false
                    this.cancelItem()
                    this.$bvToast.toast(`Item has been added.`, {title: 'Success', variant: 'success', solid: true, autoHideDelay: 4000, appendToast: false})
                    this.$refs['modal-add'].hide()
                })
                .catch((error) => {
                    console.log('Got an error while trying to save item:', error)
                    this.$bvToast.toast(`Cannot save item.`, {title: 'Error', variant: 'danger', solid: true, autoHideDelay: 4000, appendToast: false})
                    this.errorSaving = true
                })
            }
        },
        qtyMinus: function () {
            if (this.addItem.qty >= 2) {
                this.addItem.qty -= 1
            }
        },
        qtyPlus: function () {
            this.addItem.qty+=1
        }
    },
    watch: {
        'query': function () {
            this.results = ''
            this.count = 0
            this.page_size = 0
            this.fetchResults()
        }
    }
}
</script>
