<template>
  <footer class="app-footer">
    <div class="footer-left">
      <BrandLogo :size="18" :icon="12" :radius="6" />
      <span class="footer-brand-text">自动化 visio 图生成器</span>
    </div>
    <div class="footer-right">
      © 2026 C2VSDX · Powered by
      <a href="https://lazycat.cloud/" target="_blank" rel="noopener noreferrer">LightOS</a>
    </div>
  </footer>
</template>

<script setup>
import BrandLogo from './BrandLogo.vue'
</script>

<style scoped>
.app-footer {
  /* §2.1 PageFooter height: 48px，左右 padding: 24px */
  height: 48px;
  flex: none;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px;
  background: rgba(244, 247, 250, 0.75);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  border-top: 0.6px solid rgba(var(--tech-cyan-rgb), 0.12);
}

[data-theme="dark"] .app-footer {
  background: rgba(15, 22, 35, 0.88);
  border-top: 0.6px solid rgba(var(--tech-cyan-rgb), 0.08);
}

.footer-left {
  width: 320px; display: flex; align-items: center; gap: 6px; flex: none;
}
.footer-brand-text {
  font-size: 13px; font-weight: 500; color: var(--ink-3);
  font-family: var(--font-display);
}

.footer-right {
  width: 320px; text-align: right; font-size: 12px; color: var(--ink-4); flex: none;
}
.footer-right a {
  color: var(--ink-3); text-decoration: underline;
  text-underline-offset: 2px; transition: color var(--t-fast) ease;
}
.footer-right a:hover { color: var(--tech-cyan); }

@media (max-width: 900px) {
  .app-footer { padding: 0 16px; }
  .footer-left, .footer-right { width: auto; }
  .footer-right { font-size: 11px; }
}
</style>