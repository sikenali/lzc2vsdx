<template>
  <div class="result-page">
    <div v-if="!job" class="loading-state">
      <i class="ri-loader-4-line spin"></i><span>正在读取生成结果…</span>
    </div>

    <template v-else>
      <div class="result-title-row">
        <div class="title-left">
          <h1>{{ typeLabel }} · {{ job.title }}</h1>
          <span class="status-pill" :class="{ failed: job.status === 'error', cancelled: job.status === 'cancelled' }">
            <i :class="job.status === 'error' ? 'ri-error-warning-line' : job.status === 'cancelled' ? 'ri-close-circle-line' : 'ri-checkbox-circle-line'"></i>
            <span>{{ statusText }}</span>
          </span>
        </div>
        <div class="title-actions">
          <button class="soft-action" @click="regenerate">
            <i class="ri-refresh-line"></i><span>重新生成</span>
          </button>
          <button class="soft-action filled" @click="openTweak">
            <i class="ri-edit-line"></i><span>在线微调</span>
          </button>
        </div>
      </div>

      <div v-if="notice" class="notice">
        <i class="ri-information-line"></i><span>{{ notice }}</span>
      </div>

      <!-- §4.4 统计卡（Nebula：cyan/gold/coral） -->
      <div class="stats-row">
        <div class="stat-card stat-success">
          <div class="stat-texts"><strong>{{ stats.nodes }}</strong><span>图形节点</span></div>
          <i class="ri-shape-line stat-icon"></i>
        </div>
        <div class="stat-card stat-warning">
          <div class="stat-texts"><strong>{{ stats.edges }}</strong><span>连接线</span></div>
          <i class="ri-arrow-left-right-line stat-icon"></i>
        </div>
        <div class="stat-card stat-danger">
          <div class="stat-texts"><strong>{{ stats.labels }}</strong><span>文本标签</span></div>
          <i class="ri-text stat-icon"></i>
        </div>
      </div>

      <section class="preview-card card">
        <div class="preview-header">
          <div class="preview-title-left">
            <span class="title-bar"></span>
            <span class="title-text">图形预览</span>
            <span class="title-desc">已按 8px 网格自动对齐</span>
          </div>
          <div class="zoom-group">
            <button class="zoom-btn" @click="zoomOut"><i class="ri-subtract-line"></i></button>
            <button class="zoom-value" @click="zoom = 100">{{ zoom }}%</button>
            <button class="zoom-btn" @click="zoomIn"><i class="ri-add-line"></i></button>
          </div>
        </div>

        <div class="preview-canvas">
          <DiagramPreview v-if="preview" :preview="preview" :zoom="zoom" />
          <div v-else class="preview-empty">
            <i class="ri-loader-4-line spin"></i><span>预览生成中…</span>
          </div>
        </div>
      </section>

      <!-- §4.3 左下角操作按钮（紧凑版） -->
      <div class="bottom-actions">
        <button class="btn-ghost" @click="regenerate">
          <i class="ri-arrow-go-back-line"></i><span>返回重新上传</span>
        </button>
        <button class="btn-primary export-btn" @click="download">
          <i class="ri-download-line"></i><span>导出 VSDX 文件</span>
        </button>
      </div>
    </template>

    <TweakDrawer
      v-if="drawerOpen && job && job.diagram_type === 'flowchart' && job.mode === 'text'"
      :data="job.data" :saving="saving"
      @close="drawerOpen = false" @save="saveTweak"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DiagramPreview from '../components/DiagramPreview.vue'
import TweakDrawer from '../components/TweakDrawer.vue'
import { downloadUrl, getJob, tweakJob } from '../api/client'
import { loadSession, saveSession } from '../api/store'
import { toast } from '../utils/toast'

const route      = useRoute()
const router     = useRouter()
const jobId      = String(route.params.id)
const job        = ref(loadSession(jobId))
const preview    = ref(job.value?.preview || null)
const zoom       = ref(100)
const drawerOpen = ref(false)
const saving     = ref(false)
const demo       = ref(Boolean(job.value?.demo || job.value?.data?.demo))

const labels = {
  flowchart: '流程图', sequence: '时序图', composition: '组成图',
  component: '关系图', architecture: '架构图', swimlane: '泳道图',
  relationship: '关系图', org_chart: '组织架构图', mind_map: '思维导图',
  network: '网络图', other: '图表',
}
const typeLabel  = computed(() => labels[job.value?.diagram_type] || '流程图')
const statusText = computed(() => {
  if (job.value?.status === 'done')      return '已生成'
  if (job.value?.status === 'error')     return '生成失败'
  if (job.value?.status === 'cancelled') return '已取消'
  return '生成中'
})
const stats  = computed(() => job.value?.stats || { nodes: 0, edges: 0, labels: 0 })
const isDemo = computed(() => demo.value || Boolean(job.value?.data?.demo))
const notice = computed(() => {
  const p = []
  if (job.value?.error)   p.push(job.value.error)
  if (job.value?.warning) p.push(job.value.warning)
  if (isDemo.value)       p.push('当前未配置视觉模型，结果页使用演示识别数据；配置后可识别真实图片。')
  return p.join(' ')
})

async function refresh() {
  try {
    const data = await getJob(jobId)
    job.value = data
    if (data.preview) preview.value = data.preview
    saveSession(jobId, { ...loadSession(jobId), ...data, demo: demo.value })
    if (data.status === 'running') router.replace(`/${data.mode}/progress/${jobId}`)
  } catch (e) { if (!job.value) toast('error', e.message) }
}

onMounted(refresh)

function zoomIn()      { zoom.value = Math.min(200, zoom.value + 25) }
function zoomOut()     { zoom.value = Math.max(50, zoom.value - 25) }
function regenerate()  { router.push(job.value?.mode === 'image' ? '/image' : '/') }

async function download() {
  if (!job.value?.downloadable) {
    toast('warning', job.value?.warning || '当前环境无法导出 .vsdx，请在 Windows + Visio 上运行后端')
    return
  }
  try {
    const response = await fetch(downloadUrl(jobId))
    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      throw new Error(body.error || `下载失败 (${response.status})`)
    }
    const blob = await response.blob()
    const url  = URL.createObjectURL(blob)
    const link = document.createElement('a')
    const safe = (job.value.title || 'diagram').replace(/[\\/:*?"<>|]/g, '')
    link.href = url
    link.download = `${safe || 'diagram'}.vsdx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) { toast('error', e.message) }
}

function openTweak() {
  if (job.value?.mode !== 'text' || job.value?.diagram_type !== 'flowchart') {
    toast('info', '在线微调当前仅支持文本生成的流程图')
    return
  }
  drawerOpen.value = true
}

async function saveTweak(data) {
  saving.value = true
  try {
    await tweakJob(jobId, data)
    drawerOpen.value = false
    router.push(`/text/progress/${jobId}`)
  } catch (e) { toast('error', e.message) }
  finally { saving.value = false }
}
</script>

<style scoped>
.result-page { position: relative; min-height: 500px; }

.loading-state {
  display: flex; align-items: center; gap: 8px;
  color: var(--ink-4); padding: 48px 0; justify-content: center;
}

.result-title-row {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
}
.title-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
.title-left h1 {
  font-size: 22px; font-weight: 700; color: var(--ink); line-height: 1.2;
  letter-spacing: -0.01em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  font-family: var(--font-display);
}

.status-pill {
  display: inline-flex; align-items: center; gap: 4px;
  height: 24px; padding: 0 10px; border-radius: 9999px;
  background: rgba(var(--tech-cyan-rgb), 0.1); color: #008A62;
  font-size: 12px; font-weight: 500; flex: none;
}
.status-pill .ri { color: var(--color-success); font-size: 13px; }
.status-pill.failed { background: var(--color-error-soft); color: var(--color-error); }
.status-pill.failed .ri { color: var(--color-error); }
.status-pill.cancelled { background: var(--bg-soft); color: var(--ink-3); }
.status-pill.cancelled .ri { color: var(--ink-4); }

.title-actions { display: flex; align-items: center; gap: 8px; flex: none; }

.soft-action {
  display: inline-flex; align-items: center; gap: 6px;
  height: 36px; padding: 0 14px; border-radius: var(--radius-sm);
  background: var(--bg-card); border: 0.6px solid var(--line);
  color: var(--ink-3); font-size: 13px; font-weight: 500;
  font-family: var(--font-display);
  transition: background var(--t-fast) ease, color var(--t-fast) ease, border-color var(--t-fast) ease;
}
.soft-action:hover {
  color: var(--tech-cyan); border-color: rgba(var(--tech-cyan-rgb), 0.3);
  background: rgba(var(--tech-cyan-rgb), 0.06);
}
.soft-action.filled { background: var(--bg-soft); border-color: transparent; }
.soft-action.filled:hover {
  background: rgba(var(--tech-cyan-rgb), 0.06); border-color: rgba(var(--tech-cyan-rgb), 0.3); color: var(--tech-cyan);
}

.notice {
  margin-top: 12px; display: flex; align-items: center; gap: 6px;
  padding: 8px 12px; border-radius: var(--radius-sm);
  background: rgba(255, 179, 71, 0.08); color: var(--ink-3); font-size: 12px;
}
.notice .ri { color: var(--tech-gold); }

/* §4.4 统计卡（Nebula 配色） */
.stats-row { margin-top: 14px; display: flex; gap: 12px; }
.stat-card {
  flex: 1; height: 68px; border-radius: var(--radius-sm);
  padding: 0 16px; display: flex; align-items: center; justify-content: space-between;
  font-family: var(--font-display);
}
.stat-success { background: rgba(var(--tech-cyan-rgb), 0.08);  color: var(--tech-cyan); }
.stat-warning { background: rgba(255, 179, 71, 0.08); color: #FFB347; }
.stat-danger  { background: rgba(255, 77, 109, 0.08); color: #FF4D6D; }

.stat-texts { display: flex; flex-direction: column; gap: 1px; }
.stat-texts strong { font-size: 26px; font-weight: 700; line-height: 1.1; color: currentColor; }
.stat-texts span   { font-size: 13px; color: var(--ink-3); }
.stat-icon         { font-size: 22px; }

.preview-card { margin-top: 16px; padding: 18px 20px; }
.preview-header {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
}
.preview-title-left { display: flex; align-items: center; gap: 8px; }
.zoom-group { display: flex; align-items: center; gap: 4px; }

.zoom-btn {
  width: 28px; height: 28px; border-radius: var(--radius-xs);
  background: var(--bg-soft); color: var(--ink-3); font-size: 14px;
  border: none; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
  transition: background var(--t-fast) ease, color var(--t-fast) ease;
}
.zoom-btn:hover { background: rgba(var(--tech-cyan-rgb), 0.08); color: var(--tech-cyan); }

.zoom-value {
  height: 28px; padding: 0 8px; border-radius: var(--radius-xs);
  background: var(--bg-soft); color: var(--ink-3); font-size: 12px; font-weight: 500;
  border: none; cursor: default;
}

.preview-canvas {
  margin-top: 10px; padding: 14px 0;
  border-radius: var(--radius-sm);
  background: var(--bg-footer);
  border: 0.6px solid var(--line-soft);
  min-height: 320px; overflow: hidden;
}
.preview-empty {
  min-height: 300px; display: flex; align-items: center; justify-content: center;
  gap: 8px; color: var(--ink-4); font-size: 13px;
}

/* §4.3 左下角操作按钮 */
.bottom-actions {
  margin-top: 16px; display: flex; align-items: center; justify-content: center;
  gap: 10px; padding-bottom: 4px;
}
.export-btn { height: 40px; padding: 0 20px; font-size: 13px; }

.spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 760px) {
  .result-title-row { flex-direction: column; align-items: flex-start; }
  .title-left h1 { font-size: 18px; white-space: normal; }
  .stats-row { flex-direction: column; }
  .preview-title-left .title-desc { display: none; }
}
</style>