<template>
  <div class="progress-page">
    <div v-if="error" class="error-card card">
      <i class="ri-error-warning-line"></i>
      <p>{{ error }}</p>
      <button class="btn-ghost" @click="back">返回重新上传</button>
    </div>

    <template v-else>
      <section class="progress-card card">
        <ProgressSteps :stages="stages" />
        <div class="overall">
          <div class="overall-row">
            <div class="overall-left">
              <i class="ri-loader-4-line spin"></i>
              <span>整体进度</span>
            </div>
            <div class="overall-right">
              <strong>{{ progress }}%</strong>
              <span>· 预计剩余 {{ remaining }} 秒</span>
            </div>
          </div>
          <div class="track">
            <div class="fill" :style="{ width: progress + '%' }"></div>
          </div>
        </div>
      </section>

      <section class="preview-card card">
        <div class="preview-header">
          <div class="preview-title-left">
            <span class="title-bar"></span>
            <span class="title-text">图形结构构建中</span>
            <span class="title-desc">{{ mode === 'image' ? '节点与连线会自动对齐到 8px 网格' : '已解析的文本要点会自动映射为节点与连线' }}</span>
          </div>
          <div class="preview-stats">
            <span class="stat-item"><i class="ri-shape-line node"></i>节点 <strong>{{ stats.nodes }}</strong></span>
            <span class="stat-item"><i class="ri-arrow-left-right-line edge"></i>连线 <strong>{{ stats.edges }}</strong></span>
          </div>
        </div>
        <SkeletonDiagram :mode="mode" />
      </section>

      <div class="actions">
        <button class="btn-primary generating-btn" aria-disabled="true">
          <i class="ri-loader-4-line spin"></i>
          <span>生成中…</span>
        </button>
        <button class="btn-ghost cancel-btn" @click="cancel">
          <i class="ri-close-line"></i>
          <span>取消生成</span>
        </button>
      </div>
      <div class="hint-row actions-hint">
        <i class="ri-information-line"></i>
        <span>生成完成后会自动跳转到结果页，可预览并下载 .vsdx 文件</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import ProgressSteps from './ProgressSteps.vue'
import SkeletonDiagram from './SkeletonDiagram.vue'
import { useJobProgress } from '../api/useJobProgress'

const props = defineProps({
  mode: { type: String, default: 'text' },
})

const router = useRouter()
const { error, progress, remaining, stats, stages, cancel } = useJobProgress(props.mode)

function back() {
  router.push(props.mode === 'image' ? '/image' : '/')
}
</script>

<style scoped>
.progress-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.error-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--red);
  font-size: 14px;
}

.error-card .ri {
  font-size: 32px;
}

.progress-card {
  padding: 28px 32px;
}

.overall {
  margin-top: 28px;
}

.overall-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.overall-left {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--ink-3);
  font-size: 13px;
}

.overall-left .ri {
  color: var(--red);
  font-size: 14px;
}

.overall-right {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--ink-4);
}

.overall-right strong {
  color: var(--red);
  font-weight: 600;
}

.track {
  margin-top: 8px;
  height: 6px;
  border-radius: 9999px;
  background: var(--line-soft);
  overflow: hidden;
}

.fill {
  height: 100%;
  border-radius: 9999px;
  background: var(--red);
  transition: width 0.35s ease;
}

.preview-card {
  padding: 20px 24px;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.preview-title-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.preview-stats {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: none;
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--ink-4);
}

.stat-item strong {
  color: var(--ink-2);
  font-weight: 600;
}

.stat-item .node {
  color: var(--green);
  font-size: 13px;
}

.stat-item .edge {
  color: var(--gold);
  font-size: 13px;
}

.actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.generating-btn {
  min-width: 170px;
}

.cancel-btn {
  height: 52px;
  border-radius: var(--radius-btn);
}

.actions-hint {
  justify-content: center;
}

.spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 760px) {
  .progress-card {
    padding: 20px;
  }
  .preview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .title-desc {
    white-space: normal;
  }
}
</style>
