<template>
  <UiModal
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="设置中心"
    width="92vw"
    :max-width="1400"
    height="92vh"
    :radius="16"
  >
    <div class="settings-modal">
      <!-- 5.2 弹窗头部 -->
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

      <!-- 5.3 导航侧栏 + 5.4 内容区 -->
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

const props = defineProps({
  modelValue: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

/** 菜单项：本项目仅主题管理 + 关于（DESIGN §5.3 可增删）。 */
const menuItems = [
  { key: 'theme', label: '主题管理', icon: 'ri-palette-line' },
  { key: 'model', label: '模型管理', icon: 'ri-cpu-line' },
  { key: 'about', label: '关于', icon: 'ri-information-line' },
]

const active = ref('theme')

// 每次打开回到首个菜单，行为可预期。
watch(
  () => props.modelValue,
  (open) => {
    if (open) active.value = 'theme'
  }
)

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.settings-modal {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 28px 32px;
}

/* ---- 5.2 头部 ---- */
.settings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex: none;
  margin-bottom: 20px;
}

.settings-head {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.settings-icon {
  width: 48px;
  height: 48px;
  flex: none;
  border-radius: 9999px;
  background: var(--primary-soft);
  color: var(--primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.settings-title {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.2;
  color: var(--ink);
}

.settings-subtitle {
  margin-top: 2px;
  font-size: 13px;
  color: var(--ink-4);
}

.settings-close {
  width: 40px;
  height: 40px;
  flex: none;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--ink-4);
  transition: background 0.15s ease, color 0.15s ease;
}

.settings-close:hover {
  background: var(--primary-soft);
  color: var(--primary);
}

/* ---- 5.3 / 5.4 主体 ---- */
.settings-body {
  flex: 1;
  min-height: 0;
  display: flex;
  gap: 20px;
}

.settings-nav {
  width: 240px;
  flex: none;
  align-self: flex-start;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px;
  background: var(--bg-card);
  border-radius: 16px;
}

.settings-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 52px;
  padding: 0 16px;
  border-radius: 12px;
  font-size: 15px;
  color: var(--ink-2);
  text-align: left;
  transition: background 0.15s ease, color 0.15s ease;
}

.settings-nav-item i {
  flex: none;
  font-size: 20px;
}

.settings-nav-item:hover {
  background: var(--bg-soft);
}

.settings-nav-item.active {
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 500;
}

.panel-content {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
}
</style>
