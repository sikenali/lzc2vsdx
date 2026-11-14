<template>
  <div class="window-titlebar">
    <div class="tb-title">
      <span class="tb-logo"><i class="ri-target-line"></i></span>
      <span class="tb-name">C2VSDX</span>
    </div>

    <div class="tb-controls">
      <button class="tb-btn" title="设置" aria-label="打开设置中心" @click="$emit('open-settings')">
        <i class="ri-settings-3-line"></i>
      </button>
      <button class="tb-btn" title="最小化" aria-label="最小化" @click="win('minimize')">
        <i class="ri-subtract-line"></i>
      </button>
      <button class="tb-btn" :title="maximized ? '还原' : '最大化'" :aria-label="maximized ? '还原' : '最大化'" @click="win('maximizeToggle')">
        <i :class="maximized ? 'ri-restore-line' : 'ri-square-line'"></i>
      </button>
      <button class="tb-btn tb-close" title="关闭" aria-label="关闭" @click="win('close')">
        <i class="ri-close-line"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

defineEmits(['open-settings'])

const maximized = ref(false)
let offMax = null

function win(fn) {
  window.c2vsdx?.[fn]?.()
}

onMounted(() => {
  if (window.c2vsdx?.onMaximizeChange) {
    offMax = window.c2vsdx.onMaximizeChange((v) => (maximized.value = v))
  }
})
onBeforeUnmount(() => offMax?.())
</script>

<style scoped>
/* #1 自定义标题栏：36px 高，整条为拖拽区，右侧控件为 no-drag */
.window-titlebar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 36px;
  z-index: 200;                       /* 高于顶栏(100)，低于设置弹窗(1000)/Toast(10000) */
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-left: 14px;
  background: var(--bg);
  border-bottom: 0.6px solid var(--line-soft);
  -webkit-app-region: drag;           /* 整条可拖动窗口 */
  user-select: none;
  -webkit-user-select: none;
}

.tb-title {
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; color: var(--ink-4);
  font-family: var(--font-display); letter-spacing: 0.5px;
}
.tb-logo { display: inline-flex; color: var(--primary); font-size: 14px; }
.tb-name { font-weight: 600; letter-spacing: 0.3px; }

.tb-controls {
  display: flex; align-items: stretch; height: 100%;
  -webkit-app-region: no-drag;        /* 按钮不拖拽 */
}

.tb-btn {
  width: 42px;
  display: inline-flex; align-items: center; justify-content: center;
  border: none; background: transparent; cursor: pointer;
  color: var(--ink-3); font-size: 14px;
  transition: background var(--t-fast) ease, color var(--t-fast) ease;
}
.tb-btn:hover { background: var(--bg-soft); color: var(--ink); }
.tb-btn:active { background: var(--line-soft); }
.tb-btn:focus-visible { outline: none; box-shadow: inset 0 0 0 2px var(--primary); }

.tb-close:hover { background: #e81123; color: #fff; }
.tb-close:active { background: #c50f1f; }
</style>
