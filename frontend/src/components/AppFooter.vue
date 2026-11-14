<template>
  <footer class="app-footer">
    <div class="footer-left">
      <BrandLogo :size="18" :icon="12" :radius="6" />
      <span class="footer-brand-text">自动化 visio 图生成器</span>
    </div>
    <div class="footer-center">
      <button class="footer-chip" title="企业信用" @click="notify('企业信用信息')">
        <i class="ri-home-4-line"></i>
      </button>
      <button class="footer-chip" title="招标网站" @click="notify('招标网站链接')">
        <i class="ri-link"></i>
      </button>
    </div>
    <div class="footer-right">
      © 2026 C2VSDX · Powered by
      <a href="https://lazycat.cloud/" target="_blank" rel="noopener noreferrer">LightOS</a>
    </div>
  </footer>
</template>

<script setup>
import BrandLogo from './BrandLogo.vue'
import { toast } from '../utils/toast'
function notify(message) { toast('info', message) }
</script>

<style scoped>
.app-footer {
  /* §2.1 PageFooter height: 48px，左右 padding: 24px */
  height: 48px;
  flex: none;
  display: flex; align-items: center;
  padding: 0 24px;
  background: rgba(244, 247, 250, 0.75);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  border-top: 0.6px solid rgba(0, 212, 170, 0.12);
}

[data-theme="dark"] .app-footer {
  background: rgba(15, 22, 35, 0.88);
  border-top: 0.6px solid rgba(0, 245, 200, 0.08);
}

.footer-left {
  width: 320px; display: flex; align-items: center; gap: 6px; flex: none;
}
.footer-brand-text {
  font-size: 13px; font-weight: 500; color: var(--ink-3);
  font-family: var(--font-display);
}

.footer-center { flex: 1; display: flex; justify-content: center; align-items: center; gap: 10px; }

.footer-chip {
  width: 26px; height: 26px; border-radius: 9999px;
  background: var(--bg-soft); color: var(--ink-3); font-size: 13px;
  display: inline-flex; align-items: center; justify-content: center;
  border: none; cursor: pointer;
  transition: background-color var(--t-fast) var(--ease-spring), color var(--t-fast) var(--ease-spring);
}
.footer-chip:hover { background: rgba(0, 212, 170, 0.12); color: var(--tech-cyan); }
.footer-chip:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.3); }

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
@media (max-width: 640px) { .footer-center { display: none; } }
</style>