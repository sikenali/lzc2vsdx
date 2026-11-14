<template>
  <teleport to="body">
    <transition name="ui-modal">
      <div v-if="modelValue" class="ui-modal-overlay" role="dialog" aria-modal="true" :aria-label="title || undefined" @click.self="close">
        <div ref="panelRef" class="ui-modal-panel" :style="panelStyle" tabindex="-1">
          <slot />
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title:      { type: String, default: '' },
  width:      { type: String, default: '88vw' },
  maxWidth:   { type: [Number, String], default: 1100 },
  height:     { type: String, default: '86vh' },
  radius:     { type: [Number, String], default: 14 },
})

const emit = defineEmits(['update:modelValue'])
const panelRef = ref(null)
let previouslyFocused = null

const panelStyle = computed(() => ({
  width:        props.width,
  maxWidth:     typeof props.maxWidth === 'number' ? `${props.maxWidth}px` : props.maxWidth,
  height:       props.height,
  borderRadius: typeof props.radius === 'number' ? `${props.radius}px` : props.radius,
}))

function close() { if (props.modelValue) emit('update:modelValue', false) }

function getFocusable() {
  if (!panelRef.value) return []
  return Array.from(panelRef.value.querySelectorAll(
    'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
  ))
}

function onKeydown(e) {
  if (e.key === 'Escape') { close(); return }
  if (e.key !== 'Tab') return
  const f = getFocusable()
  if (!f.length) { e.preventDefault(); return }
  if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus() }
  else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus() }
}

function restoreFocus() {
  if (previouslyFocused && typeof previouslyFocused.focus === 'function') previouslyFocused.focus()
  previouslyFocused = null
}

watch(() => props.modelValue, async (open) => {
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
}, { immediate: true })

onBeforeUnmount(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.ui-modal-overlay {
  position: fixed; inset: 0; z-index: 90;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0, 0, 0, 0.55);          /* §8.1 深色遮罩 */
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
[data-theme="dark"] .ui-modal-overlay { background: rgba(0, 0, 0, 0.7); }

.ui-modal-panel {
  display: flex; flex-direction: column; overflow: hidden;
  background: rgba(10, 22, 40, 0.92);        /* §5.1 深空毛玻璃底 */
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
  border: 0.6px solid rgba(0, 212, 170, 0.12);
  /* §8.1 微弱电光青内发光边框 */
  box-shadow:
    0 8px 48px rgba(0, 0, 0, 0.55),
    inset 0 1px 0 rgba(0, 212, 170, 0.08);
}
[data-theme="dark"] .ui-modal-panel {
  background: rgba(10, 22, 40, 0.95);
  box-shadow:
    0 8px 48px rgba(0, 0, 0, 0.7),
    inset 0 1px 0 rgba(0, 245, 200, 0.06);
}

.ui-modal-panel:focus { outline: none; }

/* §8.1 入场动画：scale(0.97)→1 + opacity，200ms ease */
.ui-modal-enter-active, .ui-modal-leave-active {
  transition: opacity var(--t-modal), transform var(--t-modal);
}
.ui-modal-enter-from, .ui-modal-leave-to { opacity: 0; transform: scale(0.97); }
</style>