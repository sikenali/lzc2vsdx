<template>
  <teleport to="body">
    <transition name="ui-modal">
      <div
        v-if="modelValue"
        class="ui-modal-overlay"
        role="dialog"
        aria-modal="true"
        :aria-label="title || undefined"
        @click.self="close"
      >
        <div ref="panelRef" class="ui-modal-panel" :style="panelStyle" tabindex="-1">
          <slot />
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'

/**
 * 通用弹窗（DESIGN §8.1）：teleport 到 body，遮罩 + 居中面板。
 * - modelValue 控制开合（v-if）；ESC 与遮罩点击关闭。
 * - 打开锁定 body 滚动，关闭恢复；卸载时清理监听与滚动锁。
 * - 焦点管理：打开时焦点移入面板，Tab 在面板内循环，关闭时归还焦点。
 * - 尺寸由 width / maxWidth / height 通过 inline style 注入（不写死在 CSS）。
 */
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  width: { type: String, default: '92vw' },
  maxWidth: { type: [Number, String], default: 600 },
  height: { type: String, default: 'calc(100vh - 40px)' },
  radius: { type: [Number, String], default: 16 },
})

const emit = defineEmits(['update:modelValue'])

const panelRef = ref(null)
let previouslyFocused = null

const panelStyle = computed(() => ({
  width: props.width,
  maxWidth: typeof props.maxWidth === 'number' ? `${props.maxWidth}px` : props.maxWidth,
  height: props.height,
  borderRadius: typeof props.radius === 'number' ? `${props.radius}px` : props.radius,
}))

function close() {
  if (props.modelValue) emit('update:modelValue', false)
}

/** 面板内可聚焦元素（Tab 循环用）。 */
function getFocusable() {
  if (!panelRef.value) return []
  return Array.from(
    panelRef.value.querySelectorAll(
      'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
    )
  )
}

function onKeydown(e) {
  if (e.key === 'Escape') {
    close()
    return
  }
  if (e.key !== 'Tab') return
  const focusable = getFocusable()
  if (!focusable.length) {
    e.preventDefault()
    return
  }
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault()
    last.focus()
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault()
    first.focus()
  }
}

function restoreFocus() {
  if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
    previouslyFocused.focus()
  }
  previouslyFocused = null
}

watch(
  () => props.modelValue,
  async (open) => {
    document.body.style.overflow = open ? 'hidden' : ''
    if (open) {
      previouslyFocused = document.activeElement
      window.addEventListener('keydown', onKeydown)
      await nextTick()
      if (panelRef.value) panelRef.value.focus()
    } else {
      window.removeEventListener('keydown', onKeydown)
      restoreFocus()
    }
  },
  { immediate: true }
)

// 卸载时兜底：清理 ESC 监听与 body 滚动锁，避免泄漏。
onBeforeUnmount(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.ui-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 90;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
}

.ui-modal-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-soft);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.1);
}

.ui-modal-panel:focus {
  outline: none;
}

.ui-modal-enter-active,
.ui-modal-leave-active {
  transition: opacity 0.25s ease;
}

.ui-modal-enter-from,
.ui-modal-leave-to {
  opacity: 0;
}
</style>
