<template>
  <div class="image-page">
    <!-- §A.7 UploadCard（紧凑版：820×320，12px radius，深空毛玻璃底） -->
    <div class="upload-card card" :class="{ dragging }" @click="pickFile" @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="onDrop">
      <input ref="fileInput" type="file" accept=".png,.jpg,.jpeg,.svg,.webp" hidden @change="onInput" />

      <template v-if="!file">
        <div class="upload-icon-circle">
          <i class="ri-upload-cloud-2-line"></i>
        </div>
        <div class="upload-texts">
          <p class="upload-title">点击或拖拽图片到此处上传</p>
          <p class="upload-desc">支持 PNG/JPG/SVG/WebP，最大 10MB</p>
        </div>
        <div class="format-row">
          <span class="format-badge p">P</span>
          <span class="format-badge j">J</span>
          <span class="format-badge s">S</span>
          <span class="format-badge w">W</span>
        </div>
      </template>

      <template v-else>
        <div class="preview-wrap">
          <img :src="previewUrl" alt="上传预览" class="preview-image" />
          <button class="remove-btn" title="移除图片" @click.stop="removeFile" aria-label="移除">
            <i class="ri-close-line"></i>
          </button>
        </div>
        <div class="file-info">
          <p class="file-name">{{ file.name }}</p>
          <p class="file-size">{{ fileSize }} · 点击卡片可更换图片</p>
        </div>
      </template>
    </div>

    <div class="generate-area">
      <!-- A.11: handler 内守卫，不灰置 -->
      <button class="btn-primary generate-btn" @click="generate">
        <i :class="loading ? 'ri-loader-4-line spin' : 'ri-magic-line'"></i>
        <span>{{ loading ? '正在识别…' : '生成 VSDX 文件' }}</span>
      </button>
      <div class="hint-row">
        <i class="ri-information-line"></i>
        <span>生成后可下载 .vsdx 文件，兼容 Visio 2016 及以上版本，支持二次编辑</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { analyzeImage, createJob } from '../api/client'
import { saveLastInput, saveSession } from '../api/store'
import { toast } from '../utils/toast'

const router     = useRouter()
const file       = ref(null)
const previewUrl = ref('')
const dragging   = ref(false)
const loading    = ref(false)
const fileInput  = ref(null)
const demo       = ref(false)

const fileSize = computed(() => {
  if (!file.value) return ''
  const kb = file.value.size / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${Math.round(kb)} KB`
})

function pickFile() { if (!loading.value) fileInput.value?.click() }

function validate(candidate) {
  const okExt = /\.(png|jpe?g|svg|webp)$/i.test(candidate.name)
  if (!okExt) { toast('warning', '仅支持 PNG/JPG/SVG/WebP'); return false }
  if (candidate.size > 10 * 1024 * 1024) { toast('warning', '图片超过 10MB'); return false }
  return true
}

function accept(candidate) {
  if (!candidate || !validate(candidate)) return
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  file.value = candidate
  previewUrl.value = URL.createObjectURL(candidate)
}

function onInput(event) { accept(event.target.files?.[0]); event.target.value = '' }
function onDrop(event)  { dragging.value = false; accept(event.dataTransfer.files?.[0]) }
function removeFile() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''; file.value = null; demo.value = false
}
function onPaste(event) {
  const item = [...(event.clipboardData?.items || [])].find(i => i.type.startsWith('image/'))
  if (item) accept(item.getAsFile())
}

window.addEventListener('paste', onPaste)
onBeforeUnmount(() => {
  window.removeEventListener('paste', onPaste)
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})

async function generate() {
  /* A.11: handler 内守卫 */
  if (loading.value) { toast('info', '进行中请稍候'); return }
  if (!file.value)   { toast('warning', '请先上传图片'); return }
  loading.value = true
  try {
    let parsed
    try {
      parsed = await analyzeImage(file.value)
      demo.value = false
    } catch (error) {
      if (/视觉模型/.test(error.message)) {
        parsed = await analyzeImage(file.value, true)
        demo.value = true
        toast('info', '未配置视觉模型，当前使用演示识别数据')
      } else { throw error }
    }
    const job = await createJob({
      mode: 'image',
      diagram_type: parsed.analysis.diagram_type || 'flowchart',
      data: parsed.analysis,
      title: parsed.title,
      stats: parsed.stats,
    })
    saveSession(job.id, { ...job, demo: demo.value, analysis: parsed.analysis })
    saveLastInput({ mode: 'image', demo: demo.value })
    router.push(`/image/progress/${job.id}`)
  } catch (e) { toast('error', e.message) }
  finally { loading.value = false }
}
</script>

<style scoped>
.image-page { display: flex; flex-direction: column; align-items: center; }

/* §A.7 紧凑版 UploadCard：820×320，12px radius */
.upload-card {
  width: min(820px, calc(100vw - 48px));
  height: 320px; margin-top: 20px;
  padding: 32px 28px; border-radius: var(--radius-md);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 20px; cursor: pointer;
  background: rgba(15, 25, 40, 0.88);
  -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
  border: 0.6px solid var(--line);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: border-color var(--t-fast) var(--ease-smooth),
              background var(--t-fast) var(--ease-smooth),
              box-shadow var(--t-fast) var(--ease-smooth);
}

[data-theme="dark"] .upload-card {
  background: rgba(10, 15, 24, 0.92);
  border-color: rgba(var(--tech-cyan-rgb), 0.15);
}

/* 拖拽态：电光青边框 + 微光晕 */
.upload-card.dragging {
  border-color: var(--tech-cyan);
  background: rgba(var(--tech-cyan-rgb), 0.06);
  box-shadow: 0 0 0 2px rgba(var(--tech-cyan-rgb), 0.12), 0 4px 24px rgba(0, 0, 0, 0.08);
}

.upload-icon-circle {
  width: 72px; height: 72px; border-radius: 9999px;
  background: rgba(var(--tech-cyan-rgb), 0.1);
  border: 0.6px solid rgba(var(--tech-cyan-rgb), 0.2);
  display: flex; align-items: center; justify-content: center;
  color: var(--tech-cyan); font-size: 36px;
  box-shadow: 0 0 12px rgba(var(--tech-cyan-rgb), 0.2);
  transition: background var(--t-fast) ease;
}

.upload-texts { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.upload-title {
  font-size: 16px; font-weight: 600; color: #E8EEF5;
  font-family: var(--font-display);
}
.upload-desc { font-size: 13px; color: rgba(232, 238, 245, 0.5); }

.format-row { display: flex; gap: 10px; margin-top: 4px; }

/* §A.7 格式标签色板（科技风） */
.format-badge {
  width: 26px; height: 26px; border-radius: 5px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: #0A1628;
  font-family: var(--font-mono);
}
.format-badge.p { background: rgba(255, 77, 109, 0.85); color: #fff; }
.format-badge.j { background: rgba(var(--tech-cyan-rgb), 0.9); }
.format-badge.s { background: rgba(255, 179, 71, 0.9); }
.format-badge.w { background: rgba(74, 158, 255, 0.9); }

.preview-wrap {
  position: relative; min-width: 120px; min-height: 80px;
  max-width: 100%; max-height: 180px;
  border-radius: var(--radius-sm); overflow: hidden;
  border: 0.6px solid var(--line); background: var(--bg-soft);
  display: flex; align-items: center; justify-content: center; padding: 6px;
}
.preview-image { max-width: 100%; max-height: 176px; object-fit: contain; display: block; }

/* §A.7 replace-icon: top/right 8px, 32×32, rotate 120° on active */
.remove-btn {
  position: absolute; top: 8px; right: 8px;
  width: 32px; height: 32px; border-radius: 9999px;
  background: rgba(31, 29, 26, 0.65); color: #fff;
  display: inline-flex; align-items: center; justify-content: center; font-size: 15px;
  border: none; cursor: pointer;
  transition: transform 100ms ease-out, background-color var(--t-fast) ease;
}
.remove-btn:hover { background: rgba(31, 29, 26, 0.8); }
.remove-btn:active { transform: rotate(120deg) scale(0.95); transition-duration: 100ms; }

.file-info { text-align: center; }
.file-name {
  font-size: 14px; font-weight: 500; color: #E8EEF5;
  max-width: 700px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  font-family: var(--font-display);
}
.file-size {
  margin-top: 4px; font-size: 12px; color: rgba(232, 238, 245, 0.5);
  font-family: var(--font-mono);
}

.generate-area { margin-top: 20px; display: flex; flex-direction: column; align-items: center; }
.generate-btn  { min-width: 200px; }
.hint-row      { margin-top: 10px; text-align: center; }

.spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .upload-card { height: auto; min-height: 260px; padding: 24px 16px; }
}
</style>