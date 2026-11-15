<template>
  <span class="brand-logo" :style="{ width: size + 'px', height: size + 'px', borderRadius: radius + 'px' }">
    <!-- 层级流程图徽标：根节点在上，两个子节点在下，分叉连线（明确非回旋标） -->
    <svg :width="icon" :height="icon" viewBox="0 0 24 24" fill="none">
      <rect x="8" y="3" width="8" height="6" rx="1" stroke="currentColor" stroke-width="1.7" />
      <rect x="2" y="15" width="8" height="6" rx="1" stroke="currentColor" stroke-width="1.7" />
      <rect x="14" y="15" width="8" height="6" rx="1" stroke="currentColor" stroke-width="1.7" />
      <path d="M12 9v3M6 12h12M6 12v3M18 12v3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
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
  /* 项目徽标：电光青圆角底 + 深色图形（匹配 exe 图标 icon.svg，非裸回旋标线条） */
  background: var(--primary);
  color: var(--primary-on);
  flex: none;
}
</style>
