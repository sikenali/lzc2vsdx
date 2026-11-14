<template>
  <UiModal
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="设置中心"
    width="88vw"
    :max-width="1100"
    height="86vh"
    :radius="14"
  >
    <div class="settings-modal">
      <!-- §5.2 弹窗头部（紧凑科技版） -->
      <header class="settings-header">
        <div class="settings-head">
          <span class="settings-icon">
            <i class="ri-settings-3-line"></i>
          </span>
          <div class="settings-head-text">
            <h2 class="settings-title">设置中心</h2>
            <p class="settings-subtitle">选择要进入的设置界面</p>
          </div>
        </div>
        <button class="settings-close" type="button" aria-label="关闭" @click="close">
          <i class="ri-close-line"></i>
        </button>
      </header>

      <!-- §5.3 导航侧栏 + §5.4 内容区 -->
      <div class="settings-body">
        <nav class="settings-nav" aria-label="设置导航">
          <button
            v-for="item in menuItems"
            :key="item.key"
            type="button"
            class="settings-nav-item"
            :class="{ active: active === item.key }"
            @click="active = item.key"
          >
            <span class="settings-nav-accent"></span>
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </button>
        </nav>

        <div class="panel-content">
          <ThemeSettingsView v-if="active === 'theme'" />
          <ModelSettingsView v-else-if="active === 'model'" />
          <AboutView v-else-if="active === 'about'" />
        </div>
      </div>
    </div>
  </UiModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import UiModal from './UiModal.vue'
import ThemeSettingsView from './settings/ThemeSettingsView.vue'
import ModelSettingsView from './settings/ModelSettingsView.vue'
import AboutView from './settings/AboutView.vue'

const props = defineProps({ modelValue: { type: Boolean, default: false } })
const emit  = defineEmits(['update:modelValue'])

const active = ref('theme')

/** §5.3 菜单项（C2VSDX 保留三项） */
const menuItems = [
  { key: 'theme', label: '主题管理', icon: 'ri-palette-line' },
  { key: 'model', label: '模型管理', icon: 'ri-cpu-line' },
  { key: 'about', label: '关于',     icon: 'ri-information-line' },
]

watch(() => props.modelValue, (open) => { if (open) active.value = 'theme' })

function close() { emit('update:modelValue', false) }
</script>

<style scoped>
.settings-modal {
  flex: 1; min-height: 0; display: flex; flex-direction: column;
  padding: 16px 20px;
}

/* ── §5.2 头部（紧凑科技版：40px 图标圆、18px SemiBold）────── */
.settings-header {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; flex: none; margin-bottom: 16px; padding: 0 4px; height: 52px;
  border-bottom: 0.6px solid var(--line-soft);
}

.settings-head { display: flex; align-items: center; gap: 12px; min-width: 0; }

/* §5.2 图标圆 40px，电光青底 */
.settings-icon {
  width: 40px; height: 40px; flex: none; border-radius: 50%;
  background: rgba(0, 212, 170, 0.12);
  border: 0.6px solid rgba(0, 212, 170, 0.3);
  color: var(--tech-cyan);
  display: inline-flex; align-items: center; justify-content: center; font-size: 18px;
}

.settings-title {
  font-size: 18px; font-weight: 600; letter-spacing: 0.3px;
  line-height: 1.2; color: var(--ink);
  font-family: var(--font-display);
}
.settings-subtitle {
  margin-top: 1px; font-size: 12px; color: var(--ink-4); letter-spacing: 0.5px;
}

.settings-close {
  width: 32px; height: 32px; flex: none; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 16px; color: var(--ink-4);
  border: none; background: transparent; cursor: pointer;
  transition: background var(--t-fast) ease, color var(--t-fast) ease;
}
.settings-close:hover { background: rgba(0, 212, 170, 0.12); color: var(--tech-cyan); }
.settings-close:active { transform: scale(0.95); transition-duration: var(--t-snap); }
.settings-close:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.3); }

/* ── §5.3/§5.4 两栏紧凑布局 ─────────────────────────────── */
.settings-body {
  flex: 1; min-height: 0; display: flex; gap: 16px;
}

/* §5.3 导航侧栏 200px（跟随主题的次级面） */
.settings-nav {
  width: 200px; flex: none;
  display: flex; flex-direction: column; gap: 2px;
  padding: 12px 10px;
  border-radius: var(--radius-md);
  background: var(--bg-soft);
  border: 0.6px solid var(--line-soft);
  overflow-y: auto;
}

.settings-nav-item {
  position: relative;
  display: flex; align-items: center; gap: 10px;
  height: 42px; padding: 0 12px;
  border-radius: var(--radius-sm);
  border: none; background: transparent; cursor: pointer;
  text-align: left; font-size: 13px; letter-spacing: 0.2px;
  color: var(--ink-3);
  font-family: var(--font-display);
  transition: background var(--t-fast) var(--ease-smooth), color var(--t-fast) var(--ease-smooth);
}
.settings-nav-item i { font-size: 17px; flex-shrink: 0; }

/* §5.3 激活态：左侧竖条 3×22px 电光青发光 */
.settings-nav-accent {
  position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  width: 3px; height: 22px; border-radius: 0 2px 2px 0;
  background: var(--tech-cyan);
  box-shadow: 0 0 8px rgba(0, 212, 170, 0.5);
  opacity: 0;
  transition: opacity var(--t-fast) var(--ease-smooth);
}
.settings-nav-item.active .settings-nav-accent { opacity: 1; }

.settings-nav-item:hover { background: rgba(0, 212, 170, 0.06); }
.settings-nav-item.active {
  background: rgba(0, 212, 170, 0.08);
  color: var(--tech-cyan); font-weight: 600;
}
.settings-nav-item:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.3); }

/* §5.4 内容区 */
.panel-content {
  flex: 1; min-width: 0; overflow-y: auto;
}
</style>