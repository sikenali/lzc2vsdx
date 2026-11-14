<template>
  <div class="app-shell" :class="{ 'layout-sidebar': isSidebar, 'desktop-frame': isDesktop }">
    <SideNav v-if="isSidebar" />
    <div class="main-col">
      <!-- #1 无边框：桌面端显示自定义标题栏（设置/最小化/最大化/关闭） -->
      <WindowTitleBar v-if="isDesktop" @open-settings="showSettings = true" />
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
    <!-- §9 Toast：顶部 16px，深空毛玻璃底 -->
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
import WindowTitleBar from './components/WindowTitleBar.vue'
import { useTheme } from './stores/theme.js'

const route = useRoute()
const { theme } = useTheme()
const isWide    = computed(() => route.name === 'result')
const isSidebar = computed(() => theme.layout === 'sidebar')
// #1 桌面端（Electron）渲染自定义标题栏
const isDesktop = computed(() => !!(typeof window !== 'undefined' && window.c2vsdx?.minimize))
const showSettings = ref(false)
const toast     = ref({ type: 'info', message: '' })
let timer       = null

function onToast(event) {
  const { type = 'info', message = '' } = event.detail || {}
  toast.value = { type, message }
  /* §9 停留：success/error/warning 2.5s；info 2.0s */
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
.app-shell.layout-sidebar { flex-direction: row; }
.app-shell.layout-sidebar .app-main { justify-content: stretch; padding-left: 0; padding-right: 0; }
.main-col { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.app-container.wide { width: 100%; max-width: none; }

/* #1 桌面端：为固定标题栏预留 36px，并让内容避开（顶栏 sticky 用 --titlebar-h 对齐） */
.app-shell.desktop-frame { --titlebar-h: 36px; }
.app-shell.desktop-frame .main-col { padding-top: var(--titlebar-h); }

/* ── §9 Toast 规范（Nebula 科技风）───────────────────────── */
.toast {
  position: fixed;
  top: 16px;                          /* §9 距顶 16px */
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  display: flex; align-items: center; gap: 8px;
  width: min(380px, 90vw);
  min-width: 180px;
  padding: 10px 12px 10px 14px;
  border: 0.6px solid var(--line);
  border-radius: var(--radius-sm);    /* sm = 8px */
  background: rgba(15, 25, 40, 0.96); /* §9 深空底 */
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  font-size: 13px; color: #E8EEF5;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), var(--glow-xs);
  font-family: var(--font-display);
}

[data-theme="dark"] .toast {
  background: rgba(10, 15, 24, 0.96);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.5), var(--glow-sm);
}

.toast-bar { width: 3px; height: 18px; border-radius: 2px; flex: none; }
.toast-bar-success { background: #00D4AA; }
.toast-bar-error   { background: #FF4D6D; }
.toast-bar-warning { background: #FFB347; }
.toast-bar-info    { background: #4A9EFF; }

.toast-text { flex: 1; min-width: 0; }

.toast-close {
  width: 26px; height: 26px;
  display: inline-flex; align-items: center; justify-content: center;
  color: rgba(232, 238, 245, 0.5); font-size: 14px;
  border-radius: 50%; flex: none;
  transition: background var(--t-fast) ease, color var(--t-fast) ease;
}
.toast-close:hover { color: #E8EEF5; background: rgba(255, 255, 255, 0.1); }
.toast-close:active { transform: scale(0.93); transition-duration: var(--t-snap); }

/* §9 入场/离场：translateY(-8px)→0 / translateY(-6px)，200ms */
.toast-enter-active, .toast-leave-active {
  transition: opacity var(--t-base), transform var(--t-base);
}
.toast-enter-from { opacity: 0; transform: translate(-50%, -8px); }
.toast-leave-to   { opacity: 0; transform: translate(-50%, -6px); }
</style>