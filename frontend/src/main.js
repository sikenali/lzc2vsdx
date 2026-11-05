import { createApp } from 'vue'
import 'remixicon/fonts/remixicon.css'
import './styles/base.css'
import './stores/theme.js' // boot theme store: applies saved theme to <html> before mount
import App from './App.vue'
import router from './router'

createApp(App).use(router).mount('#app')
