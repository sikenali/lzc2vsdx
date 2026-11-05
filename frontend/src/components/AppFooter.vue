<template>
  <footer class="app-footer">
    <div class="footer-left">
      <BrandLogo :size="24" :icon="15" :radius="8" />
      <span class="footer-brand-text">自动化 visio 图生成器</span>
    </div>
    <div class="footer-center">
      <button class="footer-chip" title="企业信用" @click="notify('企业信用信息')"><i class="ri-home-4-line"></i></button>
      <button class="footer-chip" title="招标网站" @click="notify('招标网站链接')"><i class="ri-link"></i></button>
    </div>
    <div class="footer-right">© 2026 C2VSDX · Powered by <a href="https://lazycat.cloud/" target="_blank" rel="noopener noreferrer">LightOS</a></div>
  </footer>
</template>

<script setup>
import BrandLogo from './BrandLogo.vue'
import { toast } from '../utils/toast'

function notify(message) {
  toast('info', message)
}
</script>

<style scoped>
.app-footer {
  height: 58px;
  flex: none;
  display: flex;
  align-items: center;
  padding: 0 32px;
  background: var(--bg-footer);
}

.footer-left {
  width: 420px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex: none;
}

.footer-brand-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--ink-2);
}

.footer-center {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.footer-chip {
  width: 28px;
  height: 28px;
  border-radius: 9999px;
  background: var(--bg-soft);
  color: var(--ink-3);
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.footer-chip:hover {
  color: var(--red);
}

.footer-right {
  width: 420px;
  text-align: right;
  font-size: 14px;
  color: var(--ink-4);
  flex: none;
}

.footer-right a {
  color: var(--ink-3);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.footer-right a:hover {
  color: var(--red);
}

@media (max-width: 900px) {
  .app-footer {
    padding: 0 16px;
  }
  .footer-left,
  .footer-right {
    width: auto;
  }
  .footer-right {
    font-size: 12px;
  }
}

@media (max-width: 640px) {
  .footer-center {
    display: none;
  }
}
</style>
