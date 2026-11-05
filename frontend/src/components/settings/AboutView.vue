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
.about-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ---- 通用卡片 ---- */
.about-card {
  background: var(--bg-card);
  border: 0.7px solid var(--line);
  border-radius: var(--radius-card);
  padding: 20px 24px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 18px;
}

.card-title::before {
  content: '';
  width: 5px;
  height: 18px;
  border-radius: 2px;
  background: var(--primary);
  flex: none;
}

/* ---- 品牌区 ---- */
.about-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 36px 24px 28px;
}

.about-name {
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--ink);
  margin-top: 18px;
}

.about-version {
  margin-top: 8px;
  padding: 3px 12px;
  border-radius: 9999px;
  border: 0.7px solid var(--line);
  background: var(--bg-soft);
  color: var(--ink-3);
  font-size: 13px;
  font-weight: 500;
}

.about-desc {
  margin-top: 14px;
  font-size: 15px;
  color: var(--ink-3);
  line-height: 1.6;
}

/* ---- 技术栈 ---- */
.about-tech {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tech-chip {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 14px;
  border-radius: var(--radius-btn);
  border: 0.7px solid var(--line);
  background: var(--bg-soft);
  color: var(--ink-2);
  font-size: 13px;
  font-weight: 500;
}

/* ---- 仓库链接 ---- */
.about-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--primary);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: opacity 0.15s ease;
}

.about-link:hover {
  opacity: 0.8;
}

.about-link i {
  font-size: 16px;
}

/* ---- 版权行 ---- */
.about-copyright {
  text-align: center;
  font-size: 13px;
  color: var(--ink-5);
}
</style>
