<template>
  <div class="about-view">
    <!-- 品牌信息卡片（居中） -->
    <section class="about-card">
      <div class="about-badge">
        <BrandLogo :size="56" :icon="30" :radius="14" />
      </div>

      <h2 class="about-name">C2VSDX</h2>

      <p class="about-slogan">自然语言或图片，一键生成可编辑 Visio 图表</p>

      <span class="about-version">版本: v{{ VERSION }}</span>

      <a
        class="about-repo"
        :href="REPO_URL"
        target="_blank"
        rel="noopener noreferrer"
        title="访问 GitHub 仓库"
      >
        <i class="ri-github-line about-repo-icon"></i>
      </a>

      <p class="about-copy">
        © {{ YEAR }} C2VSDX · Powered by
        <a href="https://lazycat.cloud/" target="_blank" rel="noopener noreferrer">LightOS</a>
      </p>
    </section>
  </div>
</template>

<script setup>
import BrandLogo from '../BrandLogo.vue'
import pkg from '../../../../electron/package.json'

const VERSION = pkg.version
const REPO_URL = 'https://github.com/sikenali/lzc2vsdx'
const YEAR = new Date().getFullYear()
</script>

<style scoped>
.about-view {
  display: flex; flex-direction: column; gap: 14px;
}

/* ═══ 品牌信息卡片（居中） ═══ */
.about-card {
  background: var(--bg-card);
  border: 0.6px solid var(--line);
  border-radius: var(--radius-md);
  min-height: 400px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 36px 24px;
}
.about-badge {
  width: 112px; height: 112px; border-radius: 50%;
  border: 0.6px solid var(--line);
  background: var(--bg-soft);
  display: flex; align-items: center; justify-content: center;
  box-shadow: var(--glow-sm);
}
.about-name {
  margin-top: 26px; font-size: 24px; font-weight: 700;
  color: var(--ink); letter-spacing: 0.02em;
  font-family: var(--font-display);
}
.about-slogan {
  margin-top: 14px; font-size: 15px; color: var(--ink-3); text-align: center;
  line-height: 1.5;
}
.about-version {
  margin-top: 10px; font-size: 13px; color: var(--ink-4);
  font-family: var(--font-mono);
}
.about-repo {
  margin-top: 26px;
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--ink-3); text-decoration: none; cursor: pointer;
  transition: color var(--t-fast) ease, transform var(--t-fast) var(--ease-smooth);
}
.about-repo:hover { color: var(--tech-cyan); transform: translateY(-2px); }
.about-repo-icon { font-size: 34px; }
.about-copy {
  margin-top: 26px; font-size: 13px; color: var(--ink-5);
}
.about-copy a {
  color: var(--ink-3); text-decoration: underline; text-underline-offset: 2px;
}
.about-copy a:hover { color: var(--tech-cyan); }
</style>
