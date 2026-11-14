<template>
  <div class="settings-view">
    <!-- §6.1 页面头部 Card -->
    <section class="theme-card header-card">
      <div class="header-top">
        <nav class="breadcrumb" aria-label="面包屑">
          <span class="crumb">首页</span>
          <span class="crumb-sep">/</span>
          <span class="crumb">设置中心</span>
          <span class="crumb-sep">/</span>
          <span class="crumb current">主题管理</span>
        </nav>
        <button type="button" class="reset-btn" @click="reset">
          <i class="ri-restart-line"></i>
          <span>恢复默认</span>
        </button>
      </div>
      <h2 class="page-title">主题管理</h2>
      <p class="page-desc">统一切换外观底色、强调色与导航布局模式，修改即时生效</p>
    </section>

    <!-- §6.2 外观主题 Card -->
    <section class="theme-card">
      <h3 class="card-title">外观主题</h3>
      <div class="mode-grid">
        <button
          type="button"
          class="mode-card"
          :class="{ active: theme.mode === 'light' }"
          @click="setMode('light')"
        >
          <span v-if="theme.mode === 'light'" class="check-badge"><i class="ri-check-line"></i></span>
          <span class="thumb thumb-light">
            <span class="thumb-bar"></span>
            <span class="thumb-content"></span>
          </span>
          <span class="mode-name">浅色·Parchment</span>
          <span class="mode-desc">柔和米白底，标书阅读舒适</span>
        </button>

        <button
          type="button"
          class="mode-card"
          :class="{ active: theme.mode === 'dark' }"
          @click="setMode('dark')"
        >
          <span v-if="theme.mode === 'dark'" class="check-badge"><i class="ri-check-line"></i></span>
          <span class="thumb thumb-dark">
            <span class="thumb-bar"></span>
            <span class="thumb-content"></span>
          </span>
          <span class="mode-name">深色·TechDark</span>
          <span class="mode-desc">深空蓝黑，夜间作业护眼</span>
        </button>
      </div>
    </section>

    <!-- §6.3 强调色 Card（Nebula 五色） -->
    <section class="theme-card">
      <h3 class="card-title">强调色</h3>
      <div class="accent-row">
        <button
          v-for="(accent, key) in ACCENTS"
          :key="key"
          type="button"
          class="accent-item"
          @click="setAccent(key)"
        >
          <span
            class="accent-swatch"
            :class="{ active: theme.accent === key }"
            :style="{ background: accent.color }"
          >
            <i
              v-if="theme.accent === key"
              class="ri-check-line accent-check"
              :style="{ color: accent.on }"
            ></i>
          </span>
          <span class="accent-name" :class="{ active: theme.accent === key }">{{ accent.name }}</span>
        </button>
      </div>
    </section>

    <!-- §6.4 布局切换 Card -->
    <section class="theme-card">
      <h3 class="card-title">布局切换</h3>
      <div class="layout-grid">
        <button
          type="button"
          class="layout-card"
          :class="{ active: theme.layout === 'topbar' }"
          @click="switchLayout('topbar')"
        >
          <span v-if="theme.layout === 'topbar'" class="check-badge"><i class="ri-check-line"></i></span>
          <span class="mockup mock-topbar">
            <span class="mock-topbar-bar">
              <span class="nav-dot"></span><span class="nav-dot"></span><span class="nav-dot"></span>
              <span class="nav-dot"></span><span class="nav-dot"></span><span class="nav-dot"></span>
              <span class="actions-dot"></span><span class="actions-dot"></span>
            </span>
            <span class="mock-topbar-content">
              <span class="block block-wide"></span><span class="block"></span>
            </span>
          </span>
          <span class="layout-name">顶栏模式·居中导航</span>
          <span class="layout-desc">模块在顶栏居中排布，右上角统一为返回与设置</span>
        </button>

        <button
          type="button"
          class="layout-card"
          :class="{ active: theme.layout === 'sidebar' }"
          @click="switchLayout('sidebar')"
        >
          <span v-if="theme.layout === 'sidebar'" class="check-badge"><i class="ri-check-line"></i></span>
          <span class="mockup mock-sidebar">
            <span class="mock-sidebar-rail">
              <span class="rail-dot"></span><span class="rail-dot"></span><span class="rail-dot"></span>
              <span class="rail-dot"></span><span class="rail-dot"></span><span class="rail-dot"></span>
            </span>
            <span class="mock-sidebar-main">
              <span class="main-title"></span>
              <span class="block block-wide"></span><span class="block"></span>
            </span>
          </span>
          <span class="layout-name">侧边栏模式·左侧导航</span>
          <span class="layout-desc">模块在左侧竖列居中，顶栏不显示图标文字</span>
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ACCENTS, useTheme } from '../../stores/theme.js'
import { toast } from '../../utils/toast'

const { theme, setMode, setAccent, setLayout, reset } = useTheme()

/** 布局切换：写 store（实时生效）并弹出成功 toast。 */
function switchLayout(layout) {
  setLayout(layout)
  toast('success', layout === 'topbar' ? '已切换为顶栏模式' : '已切换为侧边栏模式')
}
</script>

<style scoped>
.settings-view { display: flex; flex-direction: column; gap: 14px; }

/* ---- 通用卡片（深空玻璃底适配） ---- */
.theme-card {
  background: var(--bg-card);
  border: 0.6px solid var(--line);
  border-radius: var(--radius-md);
  padding: 16px 20px;
}

.card-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600;
  color: var(--ink); margin-bottom: 14px;
  font-family: var(--font-display);
}

.card-title::before {
  content: ''; width: 4px; height: 16px; border-radius: 2px;
  background: var(--tech-cyan); flex: none;
  box-shadow: 0 0 6px rgba(0, 212, 170, 0.35);
}

/* ---- §6.1 页头卡 ---- */
.header-card { padding: 16px 20px; }
.header-top {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; margin-bottom: 12px;
}
.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--ink-5);
}
.crumb-sep { color: var(--ink-5); }
.crumb.current { color: var(--ink-3); }

/* §6.1 恢复默认按钮：36px outline */
.reset-btn {
  display: inline-flex; align-items: center; gap: 6px;
  height: 36px; padding: 0 14px;
  border-radius: var(--radius-sm);
  border: 0.6px solid rgba(0, 212, 170, 0.3);
  background: transparent; color: var(--tech-cyan);
  font-size: 12px; font-weight: 500;
  font-family: var(--font-display);
  transition: background var(--t-fast) ease, color var(--t-fast) ease;
}
.reset-btn i { font-size: 14px; }
.reset-btn:hover { background: rgba(0, 212, 170, 0.1); }

.page-title {
  font-size: 20px; font-weight: 600; letter-spacing: 0.3px;
  color: var(--ink); margin-bottom: 4px;
  font-family: var(--font-display);
}
.page-desc { font-size: 13px; color: var(--ink-4); }

/* ---- §6.2 外观主题卡 ---- */
.mode-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }

.mode-card {
  position: relative; display: flex; flex-direction: column; align-items: stretch;
  text-align: left; padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--bg-soft);
  cursor: pointer;
  transition: background var(--t-fast) ease, border-color var(--t-fast) ease;
}
.mode-card:hover { border-color: rgba(0, 212, 170, 0.3); }

/* §6.2 激活态：左侧 3×80px 电光青竖条 + 顶部微光条（无大底色块） */
.mode-card.active {
  border-color: var(--tech-cyan);
  background: rgba(0, 212, 170, 0.05);
}
.mode-card.active::before {
  content: ''; position: absolute; left: 0; top: 12px; bottom: 12px;
  width: 3px; border-radius: 0 2px 2px 0;
  background: var(--tech-cyan);
  box-shadow: 0 0 8px rgba(0, 212, 170, 0.5);
}

.check-badge {
  position: absolute; top: 8px; right: 8px; z-index: 2;
  width: 20px; height: 20px; border-radius: 9999px;
  background: var(--tech-cyan); color: #0A1628;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 12px;
  box-shadow: 0 0 8px rgba(0, 212, 170, 0.5);
}

/* §6.2 预览缩略图 100%×100px */
.thumb {
  display: block; width: 100%; height: 100px;
  border-radius: var(--radius-sm); overflow: hidden; margin-bottom: 10px;
}
.thumb-bar { display: block; height: 22px; }
.thumb-content { display: block; height: 44px; margin: 10px 10px 0; border-radius: 5px; }

/* 浅色·Parchment 预览 */
.thumb-light { background: #F4F7FA; }
.thumb-light .thumb-bar { background: rgba(0, 0, 0, 0.05); }
.thumb-light .thumb-content { background: #FFFFFF; }

/* 深色·TechDark 预览 */
.thumb-dark { background: #0A0F18; }
.thumb-dark .thumb-bar { background: var(--bg-soft); }
.thumb-dark .thumb-content { background: var(--bg-soft); }

.mode-name {
  font-size: 15px; font-weight: 600; color: var(--ink); margin-bottom: 3px;
  font-family: var(--font-display);
}
.mode-desc { font-size: 12px; color: var(--ink-4); }

/* ---- §6.3 强调色卡（64px 色盘，电光青光晕选中） ---- */
.accent-row { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 32px; }
.accent-item {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  cursor: pointer; border: none; background: transparent; padding: 0;
}

.accent-swatch {
  width: 64px; height: 64px; border-radius: 9999px;
  display: inline-flex; align-items: center; justify-content: center;
  transition: transform var(--t-fast) var(--ease-spring), box-shadow var(--t-fast) ease;
}
.accent-swatch:hover { transform: translateY(-2px); }

/* §6.3 选中：外圈电光青光晕 */
.accent-swatch.active {
  box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.2), 0 0 16px rgba(0, 212, 170, 0.4);
}
.accent-check { font-size: 20px; line-height: 1; }

.accent-name { font-size: 13px; font-weight: 400; color: var(--ink-2); }
.accent-name.active { font-weight: 700; color: var(--ink); }

/* ---- §6.4 布局切换卡 ---- */
.layout-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }

.layout-card {
  position: relative; display: flex; flex-direction: column; align-items: stretch;
  text-align: left; padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--bg-soft);
  cursor: pointer;
  transition: background var(--t-fast) ease, border-color var(--t-fast) ease;
}
.layout-card:hover { border-color: rgba(0, 212, 170, 0.3); }
.layout-card.active {
  border-color: var(--tech-cyan);
  background: rgba(0, 212, 170, 0.05);
}

/* Mockup 150px 高 */
.mockup {
  display: flex; height: 150px;
  border-radius: var(--radius-sm);
  border: 0.6px solid var(--line);
  overflow: hidden; background: var(--bg-soft); margin-bottom: 10px;
}

/* 顶栏模式 */
.mock-topbar { flex-direction: column; }
.mock-topbar-bar {
  display: flex; align-items: center; justify-content: center; gap: 5px;
  height: 22px; flex: none;
  background: var(--bg-soft);
  border-bottom: 0.6px solid var(--line-soft);
  position: relative; padding: 0 8px;
}
.nav-dot { width: 10px; height: 5px; border-radius: 3px; background: var(--ink-5); }
.actions-dot { width: 7px; height: 7px; border-radius: 9999px; background: var(--tech-cyan); margin-left: 5px; }

.mock-topbar-content { flex: 1; display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; }

/* 侧边栏模式 */
.mock-sidebar { flex-direction: row; }
.mock-sidebar-rail {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  width: 28px; flex: none;
  background: var(--bg-soft);
  border-right: 0.6px solid var(--line-soft);
  padding-top: 10px;
}
.rail-dot { width: 14px; height: 5px; border-radius: 3px; background: var(--ink-5); }
.rail-dot:first-child { background: var(--tech-cyan); height: 7px; }

.mock-sidebar-main { flex: 1; display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; }

.main-title { width: 38px; height: 7px; border-radius: 4px; background: var(--tech-cyan); margin-bottom: 2px; }
.block { width: 60%; height: 7px; border-radius: 4px; background: var(--line); }
.block-wide { width: 100%; background: var(--line-soft); }

.layout-name {
  font-size: 15px; font-weight: 600; color: var(--ink); margin-bottom: 3px;
  font-family: var(--font-display);
}
.layout-desc { font-size: 12px; color: var(--ink-4); }
</style>