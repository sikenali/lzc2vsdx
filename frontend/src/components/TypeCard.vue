<template>
  <button class="type-card" :class="{ active }" @click="$emit('select', item.key)">
    <span class="type-icon" :style="{ background: active ? 'var(--primary)' : item.iconBg }">
      <i :class="item.icon" :style="{ color: active ? 'var(--primary-on)' : item.iconColor }"></i>
    </span>
    <span class="type-texts">
      <span class="type-title">{{ item.title }}</span>
      <span class="type-desc">{{ item.desc }}</span>
    </span>
    <span class="check-badge" :class="{ active }">
      <i v-if="active" class="ri-check-line"></i>
    </span>
  </button>
</template>

<script setup>
defineProps({
  item: { type: Object, required: true },
  active: { type: Boolean, default: false },
})
defineEmits(['select'])
</script>

<style scoped>
/* DESIGN-1 §A.7 邻近组件规范：12px 圆角、0.6px 边框、token 驱动 */
.type-card {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: var(--radius-md);       /* md = 12px */
  background: var(--bg-card);
  border: 0.6px solid var(--line);
  text-align: left;
  transition: background var(--t-fast) var(--ease-smooth),
              border-color var(--t-fast) var(--ease-smooth),
              box-shadow var(--t-fast) var(--ease-smooth);
}

.type-card:hover {
  border-color: rgba(0, 212, 170, 0.3);
  box-shadow: var(--glow-xs);
}

.type-card.active {
  background: rgba(0, 212, 170, 0.06);
  border-color: var(--tech-cyan);
  box-shadow: var(--glow-xs);
}

.type-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
  font-size: 19px;
}

.type-texts {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
  min-width: 0;
}

.type-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
  font-family: var(--font-display);
}

.type-card.active .type-title {
  color: var(--tech-cyan);
  font-weight: 600;
}

.type-desc {
  font-size: 12px;
  color: var(--ink-4);
}

.check-badge {
  width: 18px;
  height: 18px;
  border-radius: 9999px;
  border: 1.3px solid var(--line);
  background: transparent;
  color: transparent;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
  transition: background var(--t-fast) ease, border-color var(--t-fast) ease;
}

.check-badge.active {
  border: none;
  background: var(--tech-cyan);
  color: #0A1628;
  box-shadow: 0 0 8px rgba(0, 212, 170, 0.4);
}
</style>