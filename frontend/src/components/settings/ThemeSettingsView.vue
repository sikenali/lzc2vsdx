<template>
  <div class="settings-view">
    <!-- 6.1 页面头部 Card -->
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

    <!-- 6.2 外观主题 Card -->
    <section class="theme-card">
      <h3 class="card-title">外观主题</h3>
      <div class="mode-grid">
        <button
          type="button"
          class="mode-card"
          :class="{ active: theme.mode === 'light' }"
          @click="setMode('light')"
        >
          <span v-if="theme.mode === 'light'" class="check-badge">
            <i class="ri-check-line"></i>
          </span>
          <span class="thumb thumb-light">
            <span class="thumb-bar"></span>
            <span class="thumb-content"></span>
          </span>
          <span class="mode-name">浅色主题·羊皮纸</span>
          <span class="mode-desc">当前默认，长时间阅读标书不易疲劳</span>
        </button>

        <button
          type="button"
          class="mode-card"
          :class="{ active: theme.mode === 'dark' }"
          @click="setMode('dark')"
        >
          <span v-if="theme.mode === 'dark'" class="check-badge">
            <i class="ri-check-line"></i>
          </span>
          <span class="thumb thumb-dark">
            <span class="thumb-bar"></span>
            <span class="thumb-content"></span>
          </span>
          <span class="mode-name">深色主题·墨夜</span>
          <span class="mode-desc">夜间或暗光环境投标作业更护眼</span>
        </button>
      </div>
    </section>

    <!-- 6.3 强调色 Card -->
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

    <!-- 6.4 布局切换 Card -->
    <section class="theme-card">
      <h3 class="card-title">布局切换</h3>
      <div class="layout-grid">
        <button
          type="button"
          class="layout-card"
          :class="{ active: theme.layout === 'topbar' }"
          @click="switchLayout('topbar')"
        >
          <span v-if="theme.layout === 'topbar'" class="check-badge">
            <i class="ri-check-line"></i>
          </span>
          <span class="mockup mock-topbar">
            <span class="mock-topbar-bar">
              <span class="nav-dot"></span>
              <span class="nav-dot"></span>
              <span class="nav-dot"></span>
              <span class="nav-dot"></span>
              <span class="nav-dot"></span>
              <span class="nav-dot"></span>
              <span class="actions-dot"></span>
              <span class="actions-dot"></span>
            </span>
            <span class="mock-topbar-content">
              <span class="block block-wide"></span>
              <span class="block"></span>
            </span>
          </span>
          <span class="layout-name">顶栏模式·居中导航</span>
          <span class="layout-desc">六大模块在顶栏居中排布，右上角统一为返回与设置</span>
        </button>

        <button
          type="button"
          class="layout-card"
          :class="{ active: theme.layout === 'sidebar' }"
          @click="switchLayout('sidebar')"
        >
          <span v-if="theme.layout === 'sidebar'" class="check-badge">
            <i class="ri-check-line"></i>
          </span>
          <span class="mockup mock-sidebar">
            <span class="mock-sidebar-rail">
              <span class="rail-dot"></span>
              <span class="rail-dot"></span>
              <span class="rail-dot"></span>
              <span class="rail-dot"></span>
              <span class="rail-dot"></span>
              <span class="rail-dot"></span>
            </span>
            <span class="mock-sidebar-main">
              <span class="main-title"></span>
              <span class="block block-wide"></span>
              <span class="block"></span>
            </span>
          </span>
          <span class="layout-name">侧边栏模式·左侧导航</span>
          <span class="layout-desc">六大模块在左侧竖列居中，顶栏不显示图标文字</span>
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
.settings-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ---- 通用卡片 ---- */
.theme-card {
  background: var(--bg-card);
  border: 0.7px solid var(--line);
  border-radius: var(--radius-card);
  padding: 20px 24px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 18px;
}

.card-title::before {
  content: '';
  width: 5px;
  height: 18px;
  border-radius: 2px;
  background: var(--primary);
  flex: none;
}

/* ---- 6.1 页头卡 ---- */
.header-card {
  padding: 20px 24px;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--ink-5);
}

.crumb-sep {
  color: var(--ink-5);
}

.crumb.current {
  color: var(--ink-3);
}

.reset-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 48px;
  padding: 0 20px;
  border-radius: var(--radius-btn);
  border: 0.7px solid var(--line);
  background: var(--bg-card);
  color: var(--ink-2);
  font-size: 14px;
  font-weight: 500;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.reset-btn i {
  font-size: 16px;
}

.reset-btn:hover {
  background: var(--bg-soft);
  color: var(--primary);
  border-color: var(--primary);
}

.page-title {
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--ink);
  margin-bottom: 6px;
}

.page-desc {
  font-size: 15px;
  color: var(--ink-3);
}

/* ---- 6.2 外观主题卡 ---- */
.mode-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.mode-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  text-align: left;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-item);
  background: var(--bg-card);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.mode-card:hover {
  border-color: var(--line-soft);
}

.mode-card.active {
  background: var(--primary-soft);
  border-color: var(--primary);
}

.check-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 2;
  width: 22px;
  height: 22px;
  border-radius: 9999px;
  background: var(--primary-fill);
  color: var(--primary-on);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

/* 预览缩略图 100%×128px：顶条 28px + 内容区 54px */
.thumb {
  display: block;
  width: 100%;
  height: 128px;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 12px;
}

.thumb-bar {
  display: block;
  height: 28px;
}

.thumb-content {
  display: block;
  height: 54px;
  margin: 14px 12px 0;
  border-radius: 6px;
}

/* 浅色主题·羊皮纸（spec 预览底色） */
.thumb-light {
  background: #f7eed4;
}

.thumb-light .thumb-bar {
  background: rgba(0, 0, 0, 0.06);
}

.thumb-light .thumb-content {
  background: rgba(255, 255, 255, 0.8);
}

/* 深色主题·墨夜（spec 预览底色） */
.thumb-dark {
  background: #333a45;
}

.thumb-dark .thumb-bar {
  background: rgba(0, 0, 0, 0.2);
}

.thumb-dark .thumb-content {
  background: rgba(255, 255, 255, 0.14);
}

.mode-name {
  font-size: 16px;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 4px;
}

.mode-desc {
  font-size: 14px;
  color: var(--ink-4);
}

/* ---- 6.3 强调色卡 ---- */
.accent-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 40px;
}

.accent-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.accent-swatch {
  width: 80px;
  height: 80px;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 0 transparent;
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.accent-swatch:hover {
  transform: translateY(-2px);
}

.accent-swatch.active {
  box-shadow: 0 0 0 3px var(--bg-card), 0 0 0 5px var(--primary);
}

.accent-check {
  font-size: 30px;
  line-height: 1;
}

.accent-name {
  font-size: 14px;
  font-weight: 400;
  color: var(--ink-2);
}

.accent-name.active {
  font-weight: 700;
  color: var(--ink);
}

/* ---- 6.4 布局切换卡 ---- */
.layout-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.layout-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  text-align: left;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-item);
  background: var(--bg-card);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.layout-card:hover {
  border-color: var(--line-soft);
}

.layout-card.active {
  background: var(--primary-soft);
  border-color: var(--primary);
}

/* Mockup 150px 高：内部色块模拟顶栏/侧边栏布局 */
.mockup {
  display: flex;
  height: 150px;
  border-radius: 10px;
  border: 0.7px solid var(--line);
  overflow: hidden;
  background: var(--bg);
  margin-bottom: 12px;
}

/* 顶栏模式 */
.mock-topbar {
  flex-direction: column;
}

.mock-topbar-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 26px;
  flex: none;
  background: var(--bg-soft);
  border-bottom: 0.7px solid var(--line);
  position: relative;
  padding: 0 8px;
}

.nav-dot {
  width: 12px;
  height: 6px;
  border-radius: 3px;
  background: var(--ink-5);
}

.actions-dot {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  background: var(--primary);
  margin-left: 6px;
}

.mock-topbar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 14px;
}

/* 侧边栏模式 */
.mock-sidebar {
  flex-direction: row;
}

.mock-sidebar-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 34px;
  flex: none;
  background: var(--bg-soft);
  border-right: 0.7px solid var(--line);
  padding-top: 12px;
}

.rail-dot {
  width: 16px;
  height: 6px;
  border-radius: 3px;
  background: var(--ink-5);
}

.rail-dot:first-child {
  background: var(--primary);
  height: 8px;
}

.mock-sidebar-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 14px;
}

.main-title {
  width: 44px;
  height: 8px;
  border-radius: 4px;
  background: var(--primary);
  margin-bottom: 2px;
}

.block {
  width: 60%;
  height: 8px;
  border-radius: 4px;
  background: var(--line);
}

.block-wide {
  width: 100%;
  background: var(--line-soft);
}

.layout-name {
  font-size: 16px;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 4px;
}

.layout-desc {
  font-size: 14px;
  color: var(--ink-4);
}
</style>
