<template>
  <span class="brand-logo" :style="{ width: size + 'px', height: size + 'px', borderRadius: radius + 'px' }">
    <svg :width="icon" :height="icon" viewBox="0 0 24 24" fill="none">
      <rect x="2" y="3" width="8" height="6" stroke="currentColor" stroke-width="1.7" />
      <rect x="14" y="3" width="8" height="6" stroke="currentColor" stroke-width="1.7" />
      <rect x="8" y="15" width="8" height="6" stroke="currentColor" stroke-width="1.7" />
      <path d="M6 9v3h12V9M12 12v3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
    </svg>
  </span>
</template>

<script setup>
defineProps({
  size: { type: Number, default: 40 },
  icon: { type: Number, default: 24 },
  radius: { type: Number, default: 12 },
})
</script>

<style scoped>
.brand-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-fill);
  color: var(--primary-on);
  flex: none;
}
</style>
