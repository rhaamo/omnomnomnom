<template>
    <div class="login">
        <b-row class="justify-content-md-center">
            <b-col col lg=3 align="center">
                <h3>Login</h3>

                <b-form @submit="doLogin">
                    <label class="sr-only" for="form-input-email">Email</label>
                    <b-input
                        id="form-input-email"
                        class="mb-2 mr-sm-2 mb-sm-0"
                        placeholder="iam@fluffy.tld"
                        v-model="email"
                    ></b-input>
                    <br>

                    <label class="sr-only" for="form-input-password">Password</label>
                    <b-input type="password" id="form-input-password" placeholder="Password" v-model="password"></b-input>
                    <br>

                    <b-button variant="primary" type="submit">Login</b-button>
                </b-form>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import Axios from 'axios'
import { mapState } from 'vuex'

export default {
    data() {
        return {
            email: '',
            password: '',
        }
    },
    computed: {
        ...mapState(['csrfToken'])
    },
    methods: {
        doLogin (event) {
            event.preventDefault()

            let userData = {
                email: this.email,
                password: this.password,
                csrf_token: this.csrfToken
            }

            Axios.post('/api/auth/login', userData).then(() => {
                // check login is good
                Axios.get('/api/auth/check_logged').then(res => {
                    if (res.data === "OK_LOGGED_IN") {
                        this.$store.commit('setLoggedIn', true)
                        this.$router.push({ name: 'Home' })
                    }
                })
                .catch((error) => {
                    console.log('Login check returned an error:', error)
                    this.$bvToast.toast(`Cannot verify login.`, {title: 'Error', variant: 'danger', solid: true, autoHideDelay: 4000, appendToast: false})
                })
            })
            .catch((error) => {
                console.log('Login error:', error)
                this.$bvToast.toast(`Cannot log in.`, {title: 'Error', variant: 'danger', solid: true, autoHideDelay: 4000, appendToast: false})
            })
        }
    }
}
</script>