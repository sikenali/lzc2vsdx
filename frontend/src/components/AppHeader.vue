<template>
  <header class="app-header" :class="{ 'sidebar-mode': isSidebar }">
    <div class="header-brand">
      <BrandLogo :size="40" :icon="24" :radius="12" />
      <span class="brand-name">C2VSDX</span>
      <span class="brand-divider"></span>
      <span class="brand-sub">{{ subtitle }}</span>
    </div>

    <span class="header-title">{{ subtitle }}</span>

    <div class="header-tabs">
      <button
        class="tab"
        :class="{ active: active === 'image' }"
        @click="go('/image')"
      >
        <i class="ri-image-line tab-icon image"></i>
        <span class="tab-label">图片生成</span>
      </button>
      <button
        class="tab"
        :class="{ active: active === 'text' }"
        @click="go('/')"
      >
        <i class="ri-file-text-line tab-icon text"></i>
        <span class="tab-label">文本生成</span>
      </button>
    </div>

    <div class="header-actions">
      <button class="round-btn" title="返回" @click="back">
        <i :class="backIcon"></i>
      </button>
      <button class="round-btn" title="设置" @click="settings">
        <i class="ri-settings-3-line"></i>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BrandLogo from './BrandLogo.vue'
import { useTheme } from '../stores/theme.js'

const route = useRoute()
const router = useRouter()
const { theme } = useTheme()
const emit = defineEmits(['open-settings'])

const active = computed(() => route.meta.tab || 'text')
const subtitle = computed(() => route.meta.subtitle || '文本生成 Visio 图')
const isSidebar = computed(() => theme.layout === 'sidebar')
const backIcon = computed(() => (route.name === 'result' ? 'ri-arrow-go-back-line' : 'ri-arrow-left-line'))

function go(path) {
  router.push(path)
}

function back() {
  if (window.history.length > 1) window.history.back()
  else router.push('/')
}

function settings() {
  emit('open-settings')
}
</script>

<style scoped>
.app-header {
  height: 72px;
  flex: none;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: var(--bg-card);
  position: relative;
  z-index: 20;
}

.header-brand {
  width: 380px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex: none;
}

.brand-name {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.2px;
  color: var(--ink);
}

.brand-divider {
  width: 3px;
  height: 20px;
  background: var(--line);
  border-radius: 2px;
  flex: none;
}

.brand-sub {
  font-size: 16px;
  color: var(--ink-3);
  white-space: nowrap;
}

/* 侧栏模式下品牌区与居中标签隐藏，仅页面标题靠左（DESIGN §2.2）。 */
.header-title {
  display: none;
  flex: 1;
  min-width: 0;
  font-size: 16px;
  color: var(--ink-3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.app-header.sidebar-mode .header-brand,
.app-header.sidebar-mode .header-tabs {
  display: none;
}

.app-header.sidebar-mode .header-title {
  display: block;
}

.header-tabs {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
}

.tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 18px;
  border-radius: 12px;
  transition: background 0.15s ease;
}

.tab:hover {
  background: rgba(251, 233, 231, 0.45);
}

.tab.active {
  background: var(--red-soft);
}

.tab-icon {
  font-size: 18px;
  line-height: 1;
}

.tab-icon.image {
  color: var(--blue);
}

.tab-icon.text {
  color: var(--gold);
}

.tab-label {
  font-size: 15px;
  font-weight: 500;
  color: var(--ink);
}

.tab.active .tab-label {
  color: var(--red);
  font-weight: 600;
}

.header-actions {
  width: 380px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  flex: none;
}

.round-btn {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  background: var(--bg-card);
  box-shadow: var(--shadow-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--ink-3);
  font-size: 18px;
}

.round-btn:hover {
  color: var(--red);
}

@media (max-width: 1100px) {
  .header-brand,
  .header-actions {
    width: 260px;
  }
  .brand-sub {
    display: none;
  }
}

@media (max-width: 760px) {
  .app-header {
    padding: 0 16px;
  }
  .header-brand,
  .header-actions {
    width: auto;
  }
  .brand-name {
    font-size: 18px;
  }
  .header-tabs {
    gap: 2px;
  }
  .tab {
    padding: 10px 12px;
  }
  .tab-label {
    font-size: 13px;
  }
}
</style>
