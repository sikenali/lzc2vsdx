<template>
  <div class="settings-view">
    <!-- 页头卡 -->
    <section class="theme-card header-card">
      <div class="header-top">
        <nav class="breadcrumb" aria-label="面包屑">
          <span class="crumb">首页</span>
          <span class="crumb-sep">/</span>
          <span class="crumb">设置中心</span>
          <span class="crumb-sep">/</span>
          <span class="crumb current">模型管理</span>
        </nav>
        <button type="button" class="reset-btn" @click="resetAll">
          <i class="ri-restart-line"></i>
          <span>恢复默认</span>
        </button>
      </div>
      <h2 class="page-title">模型管理</h2>
      <p class="page-desc">配置 OpenAI 兼容模型；未配置时图片走演示数据、文本用内置规则解析</p>
    </section>

    <!-- 视觉模型卡 -->
    <section class="theme-card">
      <h3 class="card-title">视觉模型（图片识别）</h3>
      <p class="field-note">用于识别上传图片并生成图表。留空则图片走演示数据。API Key 仅存储于本机 userData。</p>
      <div class="field-grid">
        <label class="field">
          <span class="field-label">BASE_URL</span>
          <input v-model="vision.baseUrl" class="text-input" type="text" placeholder="https://api.openai.com/v1" />
        </label>
        <label class="field">
          <span class="field-label">API_KEY</span>
          <div class="key-wrap">
            <input v-model="vision.apiKey" class="text-input" :type="visionShow ? 'text' : 'password'" placeholder="sk-…" />
            <button type="button" class="key-toggle" :aria-label="visionShow ? '隐藏' : '显示'" @click="visionShow = !visionShow">
              <i :class="visionShow ? 'ri-eye-off-line' : 'ri-eye-line'"></i>
            </button>
          </div>
        </label>
        <label class="field">
          <span class="field-label">MODEL</span>
          <input v-model="vision.model" class="text-input" type="text" placeholder="gpt-4o-mini / qwen2.5-vl" />
        </label>
      </div>
      <div class="card-actions">
        <button type="button" class="save-btn" @click="save">
          <i class="ri-save-line"></i>
          <span>保存</span>
        </button>
      </div>
    </section>

    <!-- 文本解析卡 -->
    <section class="theme-card">
      <h3 class="card-title">文本解析 LLM</h3>
      <p class="field-note">用于文本生成图表的结构化解析。留空则用内置规则解析。</p>
      <div class="field-grid">
        <label class="field">
          <span class="field-label">BASE_URL</span>
          <input v-model="llm.baseUrl" class="text-input" type="text" placeholder="https://api.openai.com/v1" />
        </label>
        <label class="field">
          <span class="field-label">API_KEY</span>
          <div class="key-wrap">
            <input v-model="llm.apiKey" class="text-input" :type="llmShow ? 'text' : 'password'" placeholder="sk-…" />
            <button type="button" class="key-toggle" :aria-label="llmShow ? '隐藏' : '显示'" @click="llmShow = !llmShow">
              <i :class="llmShow ? 'ri-eye-off-line' : 'ri-eye-line'"></i>
            </button>
          </div>
        </label>
        <label class="field">
          <span class="field-label">MODEL</span>
          <input v-model="llm.model" class="text-input" type="text" placeholder="gpt-4o-mini" />
        </label>
      </div>
      <div class="card-actions">
        <button type="button" class="save-btn" @click="save">
          <i class="ri-save-line"></i>
          <span>保存</span>
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { loadModelConfig, saveModelConfig } from '../../utils/modelConfig'
import { toast } from '../../utils/toast'

const vision = reactive({ baseUrl: '', apiKey: '', model: '' })
const llm = reactive({ baseUrl: '', apiKey: '', model: '' })
const visionShow = ref(false)
const llmShow = ref(false)
const saving = ref(false)

onMounted(async () => {
  const cfg = await loadModelConfig()
  Object.assign(vision, cfg?.vision || {})
  Object.assign(llm, cfg?.llm || {})
})

function resetAll() {
  Object.assign(vision, { baseUrl: '', apiKey: '', model: '' })
  Object.assign(llm, { baseUrl: '', apiKey: '', model: '' })
}

async function save() {
  if (saving.value) {
    toast('info', '进行中请稍候')
    return
  }
  saving.value = true
  try {
    const res = await saveModelConfig({
      vision: { ...vision },
      llm: { ...llm },
    })
    if (res?.ok === false) {
      toast('error', res.error || '保存失败')
      return
    }
    toast('success', '已保存，重启应用后生效')
  } catch (error) {
    toast('error', error.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.theme-card {
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
  margin-bottom: 8px;
}

.card-title::before {
  content: '';
  width: 5px;
  height: 18px;
  border-radius: 2px;
  background: var(--primary);
  flex: none;
}

.header-card {
  padding: 20px 24px;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--ink-5);
}

.crumb-sep {
  color: var(--ink-5);
}

.crumb.current {
  color: var(--ink-3);
}

.reset-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 48px;
  padding: 0 20px;
  border-radius: var(--radius-btn);
  border: 0.7px solid var(--line);
  background: var(--bg-card);
  color: var(--ink-2);
  font-size: 14px;
  font-weight: 500;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.reset-btn i {
  font-size: 16px;
}

.reset-btn:hover {
  background: var(--bg-soft);
  color: var(--primary);
  border-color: var(--primary);
}

.page-title {
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--ink);
  margin-bottom: 6px;
}

.page-desc {
  font-size: 15px;
  color: var(--ink-3);
}

.field-note {
  font-size: 13px;
  color: var(--ink-4);
  margin-bottom: 16px;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--ink-2);
}

.text-input {
  height: 40px;
  padding: 0 12px;
  border: 0.7px solid var(--line);
  border-radius: 10px;
  background: var(--bg-soft);
  color: var(--ink-2);
  font-size: 14px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.text-input:focus {
  border-color: var(--red);
  box-shadow: 0 0 0 3px var(--red-soft);
  outline: 2px solid var(--red);
  outline-offset: -2px;
}

.key-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.key-wrap .text-input {
  width: 100%;
  padding-right: 36px;
}

.key-toggle {
  position: absolute;
  right: 4px;
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--ink-4);
  font-size: 15px;
}

.key-toggle:hover {
  color: var(--ink);
  background: var(--bg-card);
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.save-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 44px;
  padding: 0 24px;
  border-radius: var(--radius-btn);
  background: var(--primary-fill);
  color: var(--primary-on);
  font-size: 14px;
  font-weight: 600;
  transition: transform 0.15s ease, filter 0.15s ease;
}

.save-btn i {
  font-size: 16px;
}

.save-btn:hover {
  filter: brightness(1.04);
}

.save-btn:active {
  transform: translateY(1px);
}
</style>
