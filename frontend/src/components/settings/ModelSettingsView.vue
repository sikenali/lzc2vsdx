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
.settings-view { display: flex; flex-direction: column; gap: 14px; }

.theme-card {
  background: rgba(255, 255, 255, 0.04);
  border: 0.6px solid rgba(0, 212, 170, 0.12);
  border-radius: var(--radius-md);
  padding: 16px 20px;
}

.card-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600;
  color: #E8EEF5; margin-bottom: 6px;
  font-family: var(--font-display);
}
.card-title::before {
  content: ''; width: 4px; height: 16px; border-radius: 2px;
  background: var(--tech-cyan); flex: none;
  box-shadow: 0 0 6px rgba(0, 212, 170, 0.35);
}

.header-card { padding: 16px 20px; }
.header-top {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; margin-bottom: 12px;
}
.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: rgba(232, 238, 245, 0.35);
}
.crumb-sep { color: rgba(232, 238, 245, 0.25); }
.crumb.current { color: rgba(232, 238, 245, 0.6); }

.reset-btn {
  display: inline-flex; align-items: center; gap: 6px;
  height: 36px; padding: 0 14px;
  border-radius: var(--radius-sm);
  border: 0.6px solid rgba(0, 212, 170, 0.3);
  background: transparent; color: var(--tech-cyan);
  font-size: 12px; font-weight: 500;
  font-family: var(--font-display);
  transition: background var(--t-fast) ease, color var(--t-fast) ease;
}
.reset-btn i { font-size: 14px; }
.reset-btn:hover { background: rgba(0, 212, 170, 0.1); }

.page-title {
  font-size: 20px; font-weight: 600; letter-spacing: 0.3px;
  color: #E8EEF5; margin-bottom: 4px;
  font-family: var(--font-display);
}
.page-desc { font-size: 13px; color: rgba(232, 238, 245, 0.5); }

.field-note { font-size: 12px; color: rgba(232, 238, 245, 0.5); margin-bottom: 12px; }

.field-grid {
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: 12px 14px;
}
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  font-size: 12px; font-weight: 500; color: rgba(232, 238, 245, 0.65);
  font-family: var(--font-mono);
}

/* §8.2 UiInput：38px 高，8px 圆角，focus 电光青边框 + 外发光 */
.text-input {
  height: 38px; padding: 0 12px;
  border: 0.6px solid rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-sm);
  background: rgba(0, 0, 0, 0.25);
  color: #E8EEF5;
  font-size: 13px;
  font-family: var(--font-mono);
  transition: border-color var(--t-fast) ease, box-shadow var(--t-fast) ease, background var(--t-fast) ease;
}
.text-input::placeholder { color: rgba(232, 238, 245, 0.3); }
.text-input:focus {
  border-color: var(--tech-cyan);
  background: rgba(10, 22, 40, 0.6);
  box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.15);
  outline: none;
}

.key-wrap { position: relative; display: flex; align-items: center; }
.key-wrap .text-input { width: 100%; padding-right: 36px; }

.key-toggle {
  position: absolute; right: 4px;
  width: 28px; height: 28px;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: var(--radius-xs);
  color: rgba(232, 238, 245, 0.5); font-size: 14px;
  border: none; background: transparent; cursor: pointer;
}
.key-toggle:hover { color: #E8EEF5; background: rgba(255, 255, 255, 0.08); }

.card-actions { display: flex; justify-content: flex-end; margin-top: 14px; }

.save-btn {
  display: inline-flex; align-items: center; gap: 6px;
  height: 36px; padding: 0 18px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #00D4AA, #00A878);
  color: #0A1628;
  font-size: 13px; font-weight: 600;
  font-family: var(--font-display);
  border: none; cursor: pointer;
  box-shadow: 0 2px 12px rgba(0, 212, 170, 0.25);
  transition: transform var(--t-fast) var(--ease-spring), box-shadow var(--t-fast) ease;
}
.save-btn i { font-size: 15px; }
.save-btn:hover { box-shadow: var(--glow-md); transform: translateY(-1px); }
.save-btn:active { transform: scale(0.97); transition-duration: var(--t-snap); }
</style>
