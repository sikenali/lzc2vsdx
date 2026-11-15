<template>
  <div class="about-view">
    <!-- ═══ ① Hero：品牌主视觉（懒猫风格 hero + Nebula 光晕） ═══ -->
    <section class="about-hero">
      <div class="hero-glow" aria-hidden="true"></div>
      <BrandLogo class="about-logo" :size="84" :icon="46" :radius="24" />
      <h2 class="about-name">C2VSDX</h2>
      <span class="about-version">v{{ VERSION }}</span>
      <p class="about-tagline">自然语言或图片，一键生成可编辑 Visio 图表</p>
      <p class="about-desc">
        C2VSDX 是一款将自然语言描述或截图图片转化为可编辑 Visio 图表的桌面工具。
        内置轻量级后端与 Graphviz 渲染引擎，本地优先，数据不出本机。
      </p>
    </section>

    <!-- ═══ ② 产品简介 ═══ -->
    <section class="about-card">
      <h3 class="card-title">产品简介</h3>
      <p class="about-text">
        面向需要快速产出结构图的开发者与文档团队。输入一句话描述，或上传一张架构图 / 流程图截图，
        C2VSDX 即解析结构、生成标准 Visio 文件（.vsdx），可直接在 Microsoft Visio 中打开与二次编辑。
        支持在线微调模型参数以获得更贴合预期的解析结果。
      </p>
    </section>

    <!-- ═══ ③ 核心能力 ═══ -->
    <section class="about-card">
      <h3 class="card-title">核心能力</h3>
      <div class="feature-grid">
        <div v-for="f in FEATURES" :key="f.title" class="feature-item">
          <span class="feature-icon"><i :class="f.icon"></i></span>
          <div class="feature-body">
            <h4 class="feature-title">{{ f.title }}</h4>
            <p class="feature-desc">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ ④ 技术栈 ═══ -->
    <section class="about-card">
      <h3 class="card-title">技术栈</h3>
      <div class="about-tech">
        <span v-for="tech in TECH" :key="tech" class="tech-chip">{{ tech }}</span>
      </div>
    </section>

    <!-- ═══ ⑤ 链接 ═══ -->
    <section class="about-card">
      <h3 class="card-title">链接</h3>
      <div class="about-links">
        <a class="about-link" :href="REPO_URL" target="_blank" rel="noopener noreferrer">
          <i class="ri-github-line"></i>
          <span>查看源代码</span>
          <i class="ri-external-link-line"></i>
        </a>
        <a class="about-link" href="https://lazycat.cloud/" target="_blank" rel="noopener noreferrer">
          <i class="ri-rocket-line"></i>
          <span>LightOS 平台</span>
          <i class="ri-external-link-line"></i>
        </a>
      </div>
    </section>

    <!-- ═══ ⑥ 版权 ═══ -->
    <p class="about-copyright">
      © 2026 C2VSDX · Powered by
      <a href="https://lazycat.cloud/" target="_blank" rel="noopener noreferrer">LightOS</a>
    </p>
  </div>
</template>

<script setup>
import BrandLogo from '../BrandLogo.vue'
import pkg from '../../../../electron/package.json'

const VERSION = pkg.version
const REPO_URL = 'https://github.com/sikenali/lzc2vsdx'
const TECH = ['Vue 3', 'Flask', 'Electron', 'Graphviz', 'Visio COM']

/** 核心能力（懒猫 about 分区风格：图标 + 标题 + 描述） */
const FEATURES = [
  {
    title: '文本生成',
    desc: '自然语言描述一键生成可编辑的 Visio 结构图。',
    icon: 'ri-file-text-line',
  },
  {
    title: '图片生成',
    desc: '上传架构图 / 流程图截图，识别并还原为 Visio 图表。',
    icon: 'ri-image-line',
  },
  {
    title: '在线微调',
    desc: '模型参数可视化在线微调，无需手写代码。',
    icon: 'ri-equalizer-line',
  },
  {
    title: '本地优先',
    desc: '后端与 Visio 渲染完全本地运行，数据不出本机。',
    icon: 'ri-lock-line',
  },
]
</script>

<style scoped>
.about-view { display: flex; flex-direction: column; gap: 14px; }

/* ═══ ① Hero ═══ */
.about-hero {
  position: relative; overflow: hidden;
  display: flex; flex-direction: column; align-items: center; text-align: center;
  padding: 30px 20px 26px;
  background: var(--bg-card);
  border: 0.6px solid var(--line);
  border-radius: var(--radius-md);
}
/* 顶部电光青光晕（Nebula 深空感） */
.hero-glow {
  position: absolute; top: -70px; left: 50%; transform: translateX(-50%);
  width: 320px; height: 180px; border-radius: 50%;
  background: radial-gradient(closest-side, rgba(var(--tech-cyan-rgb), 0.18), transparent);
  filter: blur(6px); pointer-events: none;
}

.about-logo { position: relative; }

.about-name {
  position: relative;
  font-size: 28px; font-weight: 700; letter-spacing: 0.03em;
  color: var(--ink); margin-top: 16px;
  font-family: var(--font-display);
}

.about-version {
  position: relative; margin-top: 10px; padding: 3px 14px; border-radius: 9999px;
  border: 0.6px solid rgba(var(--tech-cyan-rgb), 0.25);
  background: rgba(var(--tech-cyan-rgb), 0.08);
  color: var(--tech-cyan); font-size: 12px; font-weight: 500;
  font-family: var(--font-mono);
}

.about-tagline {
  position: relative; margin-top: 14px;
  font-size: 15px; font-weight: 600; color: var(--ink-2);
  font-family: var(--font-display);
}

.about-desc {
  position: relative; margin-top: 10px; max-width: 520px;
  font-size: 13px; color: var(--ink-3); line-height: 1.7;
}

/* ═══ 通用卡片 ═══ */
.about-card {
  background: var(--bg-card);
  border: 0.6px solid var(--line);
  border-radius: var(--radius-md);
  padding: 16px 20px;
}

.card-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600;
  color: var(--ink); margin-bottom: 12px;
  font-family: var(--font-display);
}
.card-title::before {
  content: ''; width: 4px; height: 16px; border-radius: 2px;
  background: var(--tech-cyan); flex: none;
  box-shadow: 0 0 6px rgba(var(--tech-cyan-rgb), 0.35);
}

/* ═══ ② 产品简介 ═══ */
.about-text {
  font-size: 13px; color: var(--ink-3); line-height: 1.8;
}

/* ═══ ③ 核心能力 ═══ */
.feature-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
}
.feature-item {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 12px 14px; border-radius: var(--radius-sm);
  background: var(--bg-soft); border: 0.6px solid var(--line-soft);
}
.feature-icon {
  flex: none; width: 34px; height: 34px; border-radius: 10px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 17px; color: var(--tech-cyan);
  background: rgba(var(--tech-cyan-rgb), 0.10);
  border: 0.6px solid rgba(var(--tech-cyan-rgb), 0.20);
}
.feature-title {
  font-size: 13px; font-weight: 600; color: var(--ink);
  font-family: var(--font-display);
}
.feature-desc {
  margin-top: 3px; font-size: 12px; color: var(--ink-4); line-height: 1.55;
}

/* ═══ ④ 技术栈 ═══ */
.about-tech { display: flex; flex-wrap: wrap; gap: 8px; }
.tech-chip {
  display: inline-flex; align-items: center; height: 30px;
  padding: 0 12px; border-radius: var(--radius-sm);
  border: 0.6px solid var(--line);
  background: var(--bg-soft);
  color: var(--ink-2);
  font-size: 12px; font-weight: 500;
  font-family: var(--font-mono);
}

/* ═══ ⑤ 链接 ═══ */
.about-links { display: flex; flex-wrap: wrap; gap: 18px; }
.about-link {
  display: inline-flex; align-items: center; gap: 8px;
  color: var(--tech-cyan); font-size: 13px; font-weight: 500;
  font-family: var(--font-display);
  text-decoration: none;
  transition: opacity var(--t-fast) ease;
}
.about-link:hover { opacity: 0.75; }
.about-link i { font-size: 15px; }
.about-link i:last-child { font-size: 12px; opacity: 0.7; }

/* ═══ ⑥ 版权 ═══ */
.about-copyright {
  text-align: center; font-size: 12px; color: var(--ink-5);
}
.about-copyright a {
  color: var(--ink-3); text-decoration: underline;
  text-underline-offset: 2px;
}
.about-copyright a:hover { color: var(--tech-cyan); }

/* 窄内容自适应：核心能力单列 */
@media (max-width: 640px) {
  .feature-grid { grid-template-columns: 1fr; }
}
</style>
