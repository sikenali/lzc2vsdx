<template>
  <div class="image-page">
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
          <button class="remove-btn" title="移除图片" @click.stop="removeFile">
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

const router = useRouter()
const file = ref(null)
const previewUrl = ref('')
const dragging = ref(false)
const loading = ref(false)
const fileInput = ref(null)
const demo = ref(false)

const fileSize = computed(() => {
  if (!file.value) return ''
  const kb = file.value.size / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${Math.round(kb)} KB`
})

function pickFile() {
  if (!loading.value) fileInput.value?.click()
}

function validate(candidate) {
  const okExt = /\.(png|jpe?g|svg|webp)$/i.test(candidate.name)
  if (!okExt) {
    toast('warning', '仅支持 PNG/JPG/SVG/WebP')
    return false
  }
  if (candidate.size > 10 * 1024 * 1024) {
    toast('warning', '图片超过 10MB')
    return false
  }
  return true
}

function accept(candidate) {
  if (!candidate || !validate(candidate)) return
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  file.value = candidate
  previewUrl.value = URL.createObjectURL(candidate)
}

function onInput(event) {
  accept(event.target.files?.[0])
  event.target.value = ''
}

function onDrop(event) {
  dragging.value = false
  accept(event.dataTransfer.files?.[0])
}

function removeFile() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  file.value = null
  demo.value = false
}

function onPaste(event) {
  const item = [...(event.clipboardData?.items || [])].find((i) => i.type.startsWith('image/'))
  if (item) accept(item.getAsFile())
}

window.addEventListener('paste', onPaste)
onBeforeUnmount(() => {
  window.removeEventListener('paste', onPaste)
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})

async function generate() {
  if (loading.value) {
    toast('info', '进行中请稍候')
    return
  }
  if (!file.value) {
    toast('warning', '请先上传图片')
    return
  }
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
      } else {
        throw error
      }
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
  } catch (error) {
    toast('error', error.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.image-page {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-card {
  width: min(875px, calc(100vw - 64px));
  height: 345px;
  margin-top: 20px;
  padding: 40px 32px;
  border-radius: var(--radius-item);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.upload-card.dragging {
  border-color: var(--red);
  background: var(--red-soft);
}

.upload-icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 9999px;
  background: var(--red-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--red);
  font-size: 40px;
}

.upload-texts {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-title {
  font-size: 18px;
  font-weight: 500;
  color: var(--ink);
}

.upload-desc {
  font-size: 14px;
  color: var(--ink-4);
}

.format-row {
  display: flex;
  gap: 12px;
}

.format-badge {
  width: 28px;
  height: 28px;
  border-radius: 5px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
}

.format-badge.p {
  background: var(--blue);
}
.format-badge.j {
  background: var(--green-ink);
}
.format-badge.s {
  background: var(--gold);
}
.format-badge.w {
  background: var(--red);
}

.preview-wrap {
  position: relative;
  min-width: 140px;
  min-height: 90px;
  max-width: 100%;
  max-height: 200px;
  border-radius: 10px;
  overflow: hidden;
  border: 0.7px solid var(--line);
  background: var(--bg-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
}

.preview-image {
  max-width: 100%;
  max-height: 198px;
  object-fit: contain;
  display: block;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border-radius: 9999px;
  background: rgba(31, 29, 26, 0.65);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.file-info {
  text-align: center;
}

.file-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--ink);
  max-width: 760px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  margin-top: 6px;
  font-size: 13px;
  color: var(--ink-4);
}

.generate-area {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.generate-btn {
  min-width: 220px;
}

.hint-row {
  margin-top: 12px;
  text-align: center;
}

.spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 900px) {
  .upload-card {
    height: auto;
    min-height: 300px;
    padding: 32px 20px;
  }
}
</style>
