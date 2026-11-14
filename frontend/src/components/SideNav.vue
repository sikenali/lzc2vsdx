<template>
  <aside class="sidenav" role="navigation" aria-label="侧边导航">
    <button type="button" class="sidenav-brand" title="返回首页" aria-label="返回首页" @click="go('/')">
      <i class="ri-target-line"></i>
    </button>

    <nav class="sidenav-nav" aria-label="工具导航">
      <button
        v-for="item in NAV"
        :key="item.key"
        type="button"
        class="sidenav-btn"
        :class="{ active: active === item.key }"
        @click="go(item.path)"
      >
        <!-- §2.2 激活态左侧竖条指示器 -->
        <span class="sidenav-accent"></span>
        <i :class="item.icon + ' sidenav-icon'"></i>
        <span class="sidenav-label">{{ item.label }}</span>
      </button>
    </nav>

    <div class="sidenav-footer">
      <span class="sidenav-version">v{{ version }}</span>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import pkg from '../../package.json'

const route = useRoute()
const router = useRouter()
const active  = computed(() => route.meta.tab || 'text')
const version = pkg.version

const NAV = [
  { key: 'text',  label: '文本生成', path: '/',      icon: 'ri-file-text-line' },
  { key: 'image', label: '图片生成', path: '/image', icon: 'ri-image-line' },
]

function go(path) { router.push(path) }
</script>

<style scoped>
.sidenav {
  width: 64px;                          /* §2.2 侧边栏宽 64px */
  flex: none;
  display: flex; flex-direction: column; align-items: center;
  min-height: 100vh;
  background: rgba(244, 247, 250, 0.88);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  border-right: 0.6px solid var(--line-soft);
}

[data-theme="dark"] .sidenav {
  background: rgba(15, 22, 35, 0.92);
  border-right: 0.6px solid var(--line);
}

/* Brand icon — RiTargetLine，电光青 */
.sidenav-brand {
  width: 48px; height: 36px; margin-top: 14px; flex: none;
  border-radius: var(--radius-sm);
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--tech-cyan); font-size: 22px;
  border: none; cursor: pointer; background: transparent;
  transition: background var(--t-fast) var(--ease-smooth);
}
.sidenav-brand:hover { background: rgba(0, 212, 170, 0.08); }

/* 导航按钮组：flex:1 撑满并垂直居中（§2.2） */
.sidenav-nav {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center;
  gap: 12px; flex: 1; padding: 0 8px;
}

.sidenav-btn {
  width: 48px; height: 48px;
  border-radius: var(--radius-sm);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 2px;
  color: var(--ink-3); border: none; cursor: pointer; background: transparent;
  position: relative;
  transition: background var(--t-fast) var(--ease-smooth), color var(--t-fast) var(--ease-smooth);
}

/* §2.2 左侧竖条指示器：3×28px 电光青发光 */
.sidenav-accent {
  position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  width: 3px; height: 28px; border-radius: 0 2px 2px 0;
  background: var(--tech-cyan);
  box-shadow: 0 0 8px rgba(0, 212, 170, 0.5);
  opacity: 0;
  transition: opacity var(--t-fast) var(--ease-smooth);
}
.sidenav-btn.active .sidenav-accent { opacity: 1; }

.sidenav-icon { font-size: 19px; line-height: 1; flex-shrink: 0; }
.sidenav-btn .ri-file-text-line { color: #FFB347; }
.sidenav-btn .ri-image-line     { color: #4A9EFF; }
.sidenav-btn.active .sidenav-icon { color: var(--tech-cyan); }

.sidenav-label {
  font-size: 10px; line-height: 1; white-space: nowrap; color: inherit;
  font-family: var(--font-display);
}

.sidenav-btn:hover { background: rgba(0, 212, 170, 0.06); }
.sidenav-btn:active { transform: scale(0.95); transition-duration: var(--t-snap); }
.sidenav-btn.active { background: rgba(0, 212, 170, 0.1); color: var(--tech-cyan); font-weight: 600; }
.sidenav-btn:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.3); }

/* 底部版本号 */
.sidenav-footer { padding-bottom: 14px; text-align: center; }
.sidenav-version {
  font-size: 9px; color: var(--ink-4); white-space: nowrap;
  font-family: var(--font-mono);
}

@media (max-width: 760px) { .sidenav { display: none; } }
</style>