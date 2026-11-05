<template>
  <button class="type-card" :class="{ active }" @click="$emit('select', item.key)">
    <span class="type-icon" :style="{ background: active ? '#fff' : item.iconBg }">
      <i :class="item.icon" :style="{ color: item.iconColor }"></i>
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
.type-card {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 14px;
  background: #fff;
  border: 0.7px solid var(--line);
  text-align: left;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.type-card:hover {
  border-color: #d9d2c2;
}

.type-card.active {
  background: var(--red-soft);
  border-color: var(--red);
}

.type-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
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
  font-size: 15px;
  font-weight: 500;
  color: var(--ink);
}

.type-card.active .type-title {
  color: var(--red);
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
  background: var(--bg-card);
  color: var(--primary-on);
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
}

.check-badge.active {
  border: none;
  background: var(--primary-fill);
}
</style>
