<template>
  <div class="about-view">
    <!-- 品牌区 -->
    <section class="about-card about-hero">
      <BrandLogo class="about-logo" :size="72" :icon="40" :radius="20" />
      <h2 class="about-name">C2VSDX</h2>
      <span class="about-version">v{{ VERSION }}</span>
      <p class="about-desc">自然语言或图片，一键生成可编辑 Visio 图表</p>
    </section>

    <!-- 技术栈 -->
    <section class="about-card">
      <h3 class="card-title">技术栈</h3>
      <div class="about-tech">
        <span v-for="tech in TECH" :key="tech" class="tech-chip">{{ tech }}</span>
      </div>
    </section>

    <!-- 仓库链接 -->
    <section class="about-card">
      <a class="about-link" :href="REPO_URL" target="_blank" rel="noopener noreferrer">
        <i class="ri-github-line"></i>
        <span>查看源代码</span>
        <i class="ri-external-link-line"></i>
      </a>
    </section>

    <!-- 版权行 -->
    <p class="about-copyright">© 2026 C2VSDX · Powered by LightOS</p>
  </div>
</template>

<script setup>
import BrandLogo from '../BrandLogo.vue'
import pkg from '../../../package.json'

const VERSION = pkg.version
const REPO_URL = 'https://github.com/yyjuan97/openvs.github.io'
const TECH = ['Vue 3', 'Flask', 'Electron', 'Graphviz', 'Visio COM']
</script>

<style scoped>
.about-view { display: flex; flex-direction: column; gap: 14px; }

/* ---- 通用卡片（深空玻璃底适配） ---- */
.about-card {
  background: rgba(255, 255, 255, 0.04);
  border: 0.6px solid rgba(0, 212, 170, 0.12);
  border-radius: var(--radius-md);
  padding: 16px 20px;
}

.card-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600;
  color: #E8EEF5; margin-bottom: 14px;
  font-family: var(--font-display);
}
.card-title::before {
  content: ''; width: 4px; height: 16px; border-radius: 2px;
  background: var(--tech-cyan); flex: none;
  box-shadow: 0 0 6px rgba(0, 212, 170, 0.35);
}

/* ---- 品牌区 ---- */
.about-hero {
  display: flex; flex-direction: column; align-items: center; text-align: center;
  padding: 28px 20px 22px;
}

.about-name {
  font-size: 24px; font-weight: 700; letter-spacing: 0.02em;
  color: #E8EEF5; margin-top: 14px;
  font-family: var(--font-display);
}

.about-version {
  margin-top: 8px; padding: 2px 12px; border-radius: 9999px;
  border: 0.6px solid rgba(0, 212, 170, 0.25);
  background: rgba(0, 212, 170, 0.08);
  color: var(--tech-cyan); font-size: 12px; font-weight: 500;
  font-family: var(--font-mono);
}

.about-desc {
  margin-top: 12px; font-size: 13px;
  color: rgba(232, 238, 245, 0.6); line-height: 1.6;
}

/* ---- 技术栈 ---- */
.about-tech { display: flex; flex-wrap: wrap; gap: 8px; }

.tech-chip {
  display: inline-flex; align-items: center; height: 30px;
  padding: 0 12px; border-radius: var(--radius-sm);
  border: 0.6px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(232, 238, 245, 0.75);
  font-size: 12px; font-weight: 500;
  font-family: var(--font-mono);
}

/* ---- 仓库链接 ---- */
.about-link {
  display: inline-flex; align-items: center; gap: 8px;
  color: var(--tech-cyan); font-size: 13px; font-weight: 500;
  font-family: var(--font-display);
  text-decoration: none;
  transition: opacity var(--t-fast) ease;
}
.about-link:hover { opacity: 0.75; }
.about-link i { font-size: 15px; }

/* ---- 版权行 ---- */
.about-copyright {
  text-align: center; font-size: 12px;
  color: rgba(232, 238, 245, 0.35);
}
</style>
