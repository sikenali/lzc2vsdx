<template>
  <aside class="sidenav">
    <button
      type="button"
      class="sidenav-brand"
      title="返回首页"
      aria-label="返回首页"
      @click="go('/')"
    >
      <i class="ri-target-line"></i>
    </button>

    <nav class="sidenav-nav" aria-label="侧边导航">
      <button
        type="button"
        class="sidenav-btn"
        :class="{ active: active === 'text' }"
        @click="go('/')"
      >
        <i class="ri-file-text-line"></i>
        <span class="sidenav-label">文本生成</span>
      </button>
      <button
        type="button"
        class="sidenav-btn"
        :class="{ active: active === 'image' }"
        @click="go('/image')"
      >
        <i class="ri-image-line"></i>
        <span class="sidenav-label">图片生成</span>
      </button>
    </nav>

    <span class="sidenav-version">v1.0.0</span>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const active = computed(() => route.meta.tab || 'text')

function go(path) {
  router.push(path)
}
</script>

<style scoped>
.sidenav {
  width: 76px;
  flex: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--bg-card);
  border-right: 0.7px solid var(--line);
}

.sidenav-brand {
  width: 56px;
  height: 56px;
  margin-top: 18px;
  flex: none;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  font-size: 26px;
  transition: background 0.15s ease;
}

.sidenav-brand:hover {
  background: var(--primary-soft);
}

.sidenav-nav {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  margin-top: 22px;
}

.sidenav-btn {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: var(--ink-3);
  transition: background 0.15s ease, color 0.15s ease;
}

.sidenav-btn i {
  font-size: 22px;
  line-height: 1;
}

.sidenav-label {
  font-size: 11px;
  line-height: 1;
  white-space: nowrap;
}

.sidenav-btn:hover {
  background: var(--primary-soft);
}

.sidenav-btn.active {
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 500;
}

.sidenav-version {
  margin-top: auto;
  padding-bottom: 18px;
  font-size: 10.5px;
  color: var(--ink-4);
  white-space: nowrap;
}
</style>
