<template>
  <div class="app-shell" :class="{ 'layout-sidebar': isSidebar }">
    <SideNav v-if="isSidebar" />
    <div class="main-col">
      <AppHeader @open-settings="showSettings = true" />
      <main class="app-main">
        <div class="app-container" :class="{ wide: isWide }">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
      <AppFooter />
    </div>
    <SettingsModal v-model="showSettings" />
    <transition name="toast">
      <div v-if="toast.message" class="toast" :class="'toast-' + toast.type" role="status">
        <span class="toast-bar" :class="'toast-bar-' + toast.type"></span>
        <span class="toast-text">{{ toast.message }}</span>
        <button class="toast-close" aria-label="关闭提示" @click="closeToast">
          <i class="ri-close-line"></i>
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import SettingsModal from './components/SettingsModal.vue'
import SideNav from './components/SideNav.vue'
import { useTheme } from './stores/theme.js'

const route = useRoute()
const { theme } = useTheme()
const isWide = computed(() => route.name === 'result')
const isSidebar = computed(() => theme.layout === 'sidebar')
const showSettings = ref(false)
const toast = ref({ type: 'info', message: '' })
let timer = null

function onToast(event) {
  const { type = 'info', message = '' } = event.detail || {}
  toast.value = { type, message }
  const duration = type === 'info' ? 2000 : 2500
  clearTimeout(timer)
  timer = setTimeout(() => (toast.value = { type: 'info', message: '' }), duration)
}

function closeToast() {
  clearTimeout(timer)
  toast.value = { type: 'info', message: '' }
}

onMounted(() => window.addEventListener('c2vsdx-toast', onToast))
onBeforeUnmount(() => {
  window.removeEventListener('c2vsdx-toast', onToast)
  clearTimeout(timer)
})
</script>

<style scoped>
.app-shell.layout-sidebar {
  flex-direction: row;
}

.main-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.app-container.wide {
  width: 100%;
  max-width: none;
}

.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  display: flex;
  align-items: center;
  gap: 10px;
  width: min(420px, 90vw);
  min-width: 200px;
  padding: 12px 16px 12px 18px;
  border: 0.7px solid var(--line);
  border-radius: 10px;
  background: var(--bg-card);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
  font-size: 13px;
  color: var(--ink);
}

.toast-bar {
  width: 3px;
  height: 20px;
  border-radius: 2px;
  flex: none;
}

.toast-bar-success {
  background: var(--green);
}

.toast-bar-error {
  background: var(--red);
}

.toast-bar-warning {
  background: var(--orange);
}

.toast-bar-info {
  background: var(--blue);
}

.toast-text {
  flex: 1;
  min-width: 0;
}

.toast-close {
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--ink-4);
  font-size: 15px;
  flex: none;
}

.toast-close:hover {
  color: var(--ink);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -8px);
}

.toast-enter-from {
  transform: translate(-50%, -12px);
}
</style>
