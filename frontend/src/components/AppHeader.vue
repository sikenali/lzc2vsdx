<template>
  <header class="app-header" :class="{ 'sidebar-mode': isSidebar }">
    <div class="header-brand" @click="go('/')">
      <BrandLogo :size="36" :icon="22" :radius="8" />
      <span class="brand-name">C2VSDX</span>
      <span class="brand-divider"></span>
      <span class="brand-sub">{{ subtitle }}</span>
    </div>

    <span class="header-title">{{ subtitle }}</span>

    <!-- §2.3 标签区：底部发光滑条指示器 -->
    <div class="header-tabs-wrapper">
      <nav class="nav-center" role="navigation" aria-label="主工具导航">
        <div class="nav-indicator" :style="indicatorStyle"></div>
        <button
          v-for="(tab, i) in TABS"
          :key="tab.key"
          ref="tabRefs"
          class="nav-item"
          :class="{ active: active === tab.key, [`color-${tab.colorName}`]: true }"
          :aria-current="active === tab.key ? 'page' : undefined"
          @click="go(tab.path)"
        >
          <i :class="tab.icon + ' nav-icon'"></i>
          <span class="nav-label">{{ tab.label }}</span>
        </button>
      </nav>
    </div>

    <!-- 返回/设置按钮已移除：设置移至自定义标题栏（桌面），返回由页面内导航承担 -->
    <div class="header-actions" aria-hidden="true"></div>
  </header>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BrandLogo from './BrandLogo.vue'
import { useTheme } from '../stores/theme.js'

const route = useRoute()
const router = useRouter()
const { theme } = useTheme()

// TABS 注册表（C2VSDX 两种模式，配色对应 §2.3.2 brand 色板）
const TABS = [
  { key: 'text',  label: '文本生成', path: '/',      icon: 'ri-file-text-line', colorName: 'gold' },
  { key: 'image', label: '图片生成', path: '/image', icon: 'ri-image-line',     colorName: 'blue' },
]

const active    = computed(() => route.meta.tab || 'text')
const subtitle  = computed(() => route.meta.subtitle || '文本生成 Visio 图')
const isSidebar = computed(() => theme.layout === 'sidebar')

// §2.3 底部滑动指示器（发光条跟随激活标签）
const tabRefs = ref([])
const indicator = ref({ x: 0, w: 0 })
const indicatorStyle = computed(() => ({
  transform: `translateX(${indicator.value.x}px)`,
  width: `${indicator.value.w}px`,
}))

function setIndicator(index) {
  const el = tabRefs.value[index]
  if (!el) return
  indicator.value = { x: el.offsetLeft, w: el.offsetWidth }
}

watch(active, async (val) => {
  if (!val) return
  await nextTick()
  setIndicator(TABS.findIndex(t => t.key === val))
})

onMounted(async () => {
  await nextTick()
  setIndicator(TABS.findIndex(t => t.key === active.value))
})

function go(path) { router.push(path) }
</script>

<style scoped>
.app-header {
  /* §2.1 TopNav height: 64px，左右 padding: 20px，毛玻璃 + 发光分割线 */
  height: 64px;
  flex: none;
  display: flex; align-items: center;
  padding: 0 20px;
  background: rgba(244, 247, 250, 0.82);
  -webkit-backdrop-filter: blur(16px);
  backdrop-filter: blur(16px);
  position: sticky; top: var(--titlebar-h, 0px); z-index: 100;
  border-bottom: 0.6px solid transparent;
  /* 电光青微发光分割线 */
  border-image: linear-gradient(90deg, transparent, rgba(var(--tech-cyan-rgb),0.25) 50%, transparent) 1;
}

[data-theme="dark"] .app-header {
  background: rgba(15, 22, 35, 0.88);
  border-image: linear-gradient(90deg, transparent, rgba(var(--tech-cyan-rgb),0.18) 50%, transparent) 1;
}

.header-brand {
  width: 280px; display: flex; align-items: center; gap: 10px;
  flex: none; cursor: pointer;
}

.brand-name {
  font-size: 17px; font-weight: 700; letter-spacing: normal; color: var(--ink);
  font-family: var(--font-display);
  transition: color var(--t-fast) ease, text-shadow var(--t-fast) ease;
}
.brand-name:hover {
  color: var(--tech-cyan);
  text-shadow: 0 0 8px rgba(var(--tech-cyan-rgb), 0.5);
}

.brand-divider { width: 1.5px; height: 18px; background: var(--line); flex: none; }

.brand-sub {
  font-size: 14px; color: var(--ink-3);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* sidebar mode: hide brand tabs, show only title (§2.2) */
.header-title {
  display: none; flex: 1; min-width: 0;
  font-size: 14px; color: var(--ink-3);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.app-header.sidebar-mode .header-brand,
.app-header.sidebar-mode .header-tabs-wrapper { display: none; }
.app-header.sidebar-mode .header-title { display: block; }

/* ── §2.3 标签区 + 底部发光滑条 ─────────────────────────────── */
.header-tabs-wrapper { flex: 1; display: flex; justify-content: center; }

.nav-center {
  display: flex; align-items: center; gap: 4px; position: relative;
}

.nav-indicator {
  position: absolute; bottom: -2px; left: 0;
  height: 2.5px; border-radius: 2px 2px 0 0;
  background: linear-gradient(90deg, var(--tech-cyan), var(--tech-blue));
  box-shadow: 0 0 8px rgba(var(--tech-cyan-rgb),0.5), 0 1px 3px rgba(var(--tech-cyan-rgb),0.3);
  transition: transform var(--t-fast) var(--ease-spring),
              width     var(--t-fast) var(--ease-spring);
}

.nav-item {
  display: flex; align-items: center; justify-content: center;
  gap: 6px; padding: 8px 14px; height: 34px;
  border-radius: var(--radius-md);
  cursor: pointer; border: none; background: transparent;
  transition:
    background-color var(--t-fast) var(--ease-smooth),
    color            var(--t-fast) var(--ease-smooth),
    transform        var(--t-fast) var(--ease-spring);
  font-family: var(--font-display);
  line-height: 1.2; letter-spacing: 0.2px;
  color: var(--ink);
  font-size: 13px; font-weight: 500;
  position: relative;
  will-change: transform;
}

/* hover 顶部微光条 */
.nav-item::before {
  content: ''; position: absolute; top: 0; left: 15%; right: 15%;
  height: 0.6px; opacity: 0;
  background: linear-gradient(90deg, transparent, rgba(var(--tech-cyan-rgb),0.6), transparent);
  transition: opacity var(--t-fast) ease;
}
.nav-item:hover::before { opacity: 1; }
.nav-item:hover { background: rgba(var(--tech-cyan-rgb),0.07); transform: translateY(-1px); }
.nav-item:active { transform: scale(0.97); transition-duration: var(--t-snap); }
.nav-item:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(var(--tech-cyan-rgb),0.3); }

/* 激活态：文字变电光青 */
.nav-item.active { color: var(--tech-cyan); font-weight: 600; }

.nav-icon  { font-size: 16px; flex-shrink: 0; line-height: 1; }
.nav-label { font-size: 13px; font-weight: 500; letter-spacing: 0.2px; }

/* 品牌色图标 */
.nav-item.color-gold .nav-icon { color: #FFB347; }
.nav-item.color-blue .nav-icon { color: #4A9EFF; }
.nav-item.active.color-gold .nav-icon { color: var(--tech-cyan); }
.nav-item.active.color-blue .nav-icon { color: var(--tech-cyan); }

/* ── §2.3.4 右侧空占位（与左侧 brand 等宽，保持标签居中）──── */
.header-actions {
  width: 280px; display: flex; justify-content: flex-end; align-items: center; gap: 6px;
  flex: none;
}

@media (max-width: 1100px) {
  .header-brand, .header-actions { width: auto; }
  .brand-sub { display: none; }
}
@media (max-width: 760px) {
  .app-header { padding: 0 12px; }
  .brand-name { font-size: 16px; }
  .nav-label { font-size: 12px; }
  .nav-icon { font-size: 14px; }
}
</style>