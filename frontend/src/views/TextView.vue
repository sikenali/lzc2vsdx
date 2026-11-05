<template>
  <div class="text-page">
    <div class="left-column">
      <div class="type-header">
        <div class="section-title-row">
          <span class="title-bar"></span>
          <span class="title-text">选择图表类型</span>
          <span class="title-desc">单选，切换即重新生成</span>
        </div>
        <div class="selected-count">
          <span>已选</span>
          <strong>1</strong>
          <span>项</span>
        </div>
      </div>

      <div class="type-list">
        <TypeCard
          v-for="item in types"
          :key="item.key"
          :item="item"
          :active="selected === item.key"
          @select="selected = $event"
        />
      </div>
    </div>

    <div class="right-column">
      <section class="editor-card card">
        <div class="editor-header">
          <div class="editor-title">
            <i class="ri-file-text-line"></i>
            <span>需求描述文本</span>
          </div>
          <span class="editor-count">{{ charCount }} 字 · {{ paragraphCount }} 段</span>
        </div>

        <div class="editor-body" @click="startEdit">
          <div v-if="!editing" class="text-display">
            <template v-if="paragraphs.length">
              <p class="text-title-line">{{ paragraphs[0] }}</p>
              <p v-for="(p, i) in paragraphs.slice(1)" :key="i" class="text-paragraph">{{ p }}</p>
              <p class="text-placeholder">继续输入你的业务流程描述，或粘贴已有的需求文档…</p>
            </template>
            <p v-else class="text-placeholder">继续输入你的业务流程描述，或粘贴已有的需求文档…</p>
          </div>
          <textarea
            v-else
            ref="textarea"
            v-model="text"
            class="text-input"
            spellcheck="false"
            @blur="editing = false"
          ></textarea>
        </div>

        <div class="editor-divider"></div>
        <div class="editor-footer">
          <div class="model-select-wrap">
            <select v-model="model" class="model-select">
              <option value="c2vsdx-graph-v2">c2vsdx-graph v2</option>
              <option value="c2vsdx-graph-v1">c2vsdx-graph v1</option>
            </select>
            <i class="ri-arrow-down-s-line select-arrow"></i>
          </div>
          <button class="clear-btn" @click="clearText">
            <i class="ri-delete-bin-line"></i>
            <span>清空</span>
          </button>
        </div>
      </section>

      <div class="generate-area">
        <button class="btn-primary generate-btn" @click="generate">
          <i :class="loading ? 'ri-loader-4-line spin' : 'ri-magic-line'"></i>
          <span>{{ loading ? '正在解析…' : '生成 VSDX 文件' }}</span>
        </button>
        <div class="hint-row generate-hint">
          <i class="ri-information-line"></i>
          <span>生成后可下载 .vsdx 文件，兼容 Visio 2016 及以上版本，支持二次编辑</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import TypeCard from '../components/TypeCard.vue'
import { analyzeText, createJob } from '../api/client'
import { loadLastInput, saveSession, saveLastInput } from '../api/store'
import { toast } from '../utils/toast'

const router = useRouter()
const types = [
  { key: 'flowchart', title: '流程图', desc: '节点流转与分支', icon: 'ri-flow-chart', iconColor: '#BE3B2E', iconBg: '#FFFFFF' },
  { key: 'sequence', title: '时序图', desc: '参与者消息交互', icon: 'ri-time-line', iconColor: '#4A72A8', iconBg: '#E8F0F8' },
  { key: 'composition', title: '组成图', desc: '模块构成拆解', icon: 'ri-stack-line', iconColor: '#D3A93F', iconBg: '#F7EEE0' },
  { key: 'component', title: '关系图', desc: '实体关联映射', icon: 'ri-links-line', iconColor: '#3E8C6E', iconBg: '#E4F0EA' },
  { key: 'architecture', title: '架构图', desc: '分层系统架构', icon: 'ri-building-2-line', iconColor: '#2F3640', iconBg: '#EDE9E0' },
  { key: 'swimlane', title: '泳道图', desc: '跨角色流程泳道', icon: 'ri-layout-column-line', iconColor: '#3A5C96', iconBg: '#E8F0F8' },
]

const SAMPLE = `用户登录流程
用户打开 App 后进入登录页，页面展示手机号输入框、验证码输入框以及「登录」按钮，并在底部提供「遇到问题？」帮助入口。
用户输入手机号后点击「获取验证码」，前端校验手机号格式；校验通过后，系统调用短信服务下发 6 位动态验证码，验证码有效期 60 秒并开始倒计时。
用户在 60 秒内填写验证码并点击「登录」，前端完成非空校验后调用登录接口。
登录接口依次校验：若手机号未注册，返回「账号不存在」并引导注册；若验证码错误，返回剩余重试次数（最多 5 次）；若账号已被锁定，提示联系客服；以上校验均通过则签发 Token。
Token 写入本地安全缓存后，系统并行请求用户信息接口与权限接口，完成后跳转至首页。
首页加载完成后，系统异步上报登录埋点日志；若 Token 过期或被服务端注销，则拦截请求并回到登录页。`

const text = ref(SAMPLE)
const selected = ref('flowchart')
const model = ref('c2vsdx-graph-v2')
const editing = ref(false)
const loading = ref(false)
const textarea = ref(null)

onMounted(() => {
  const last = loadLastInput()
  if (last?.mode === 'text' && last.text) {
    text.value = last.text
    selected.value = last.diagram_type || 'flowchart'
  }
})

const paragraphs = computed(() => text.value.split('\n').map((p) => p.trim()).filter(Boolean))
const charCount = computed(() => text.value.replace(/\s/g, '').length)
const paragraphCount = computed(() => paragraphs.value.length)

async function startEdit() {
  if (editing.value) return
  editing.value = true
  await nextTick()
  textarea.value?.focus()
  const len = textarea.value.value.length
  textarea.value.setSelectionRange(len, len)
}

function clearText() {
  text.value = ''
  editing.value = true
  nextTick(() => textarea.value?.focus())
}

async function generate() {
  if (loading.value) {
    toast('info', '进行中请稍候')
    return
  }
  if (!text.value.trim()) {
    toast('warning', '请先输入需求描述')
    return
  }
  loading.value = true
  try {
    const parsed = await analyzeText(selected.value, text.value, model.value)
    saveLastInput({ mode: 'text', diagram_type: selected.value, text: text.value })
    const job = await createJob({
      mode: 'text',
      diagram_type: selected.value,
      data: parsed.data,
      title: parsed.title,
      stats: parsed.stats,
    })
    saveSession(job.id, { ...job, diagram_type: selected.value, data: parsed.data })
    router.push(`/text/progress/${job.id}`)
  } catch (error) {
    toast('error', error.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.text-page {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.left-column {
  width: 360px;
  flex: none;
  padding-top: 20px;
}

.right-column {
  flex: 1;
  min-width: 0;
  padding-top: 20px;
}

.type-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.selected-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--ink-4);
}

.selected-count strong {
  color: var(--red);
  font-weight: 600;
}

.type-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.editor-card {
  height: 512px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-header {
  height: 52px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.editor-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
}

.editor-title .ri {
  color: var(--red);
  font-size: 18px;
}

.editor-count {
  font-size: 13px;
  color: var(--ink-4);
}

.editor-body {
  flex: 1;
  min-height: 0;
  padding: 20px 24px;
  overflow-y: auto;
  cursor: text;
}

.text-title-line {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.2;
  color: var(--ink);
  margin-bottom: 12px;
}

.text-paragraph {
  font-size: 14px;
  line-height: 1.36;
  color: var(--ink-2);
  margin-bottom: 8px;
}

.text-placeholder {
  font-size: 14px;
  line-height: 1.36;
  color: var(--ink-6);
  margin-top: 8px;
}

.text-input {
  width: 100%;
  height: 100%;
  min-height: 380px;
  resize: none;
  font-size: 14px;
  line-height: 1.45;
  color: var(--ink-2);
  background: transparent;
}

.text-input:focus {
  outline: 2px solid var(--red);
  outline-offset: -2px;
  box-shadow: 0 0 0 3px var(--red-soft);
  border-radius: 4px;
}

.model-select:focus {
  border-color: var(--red);
  box-shadow: 0 0 0 3px var(--red-soft);
  border-radius: 10px;
  outline: 2px solid var(--red);
  outline-offset: -2px;
}

.editor-divider {
  height: 1px;
  background: var(--line-soft);
  flex: none;
}

.editor-footer {
  height: 52px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-footer);
}

.model-select-wrap {
  position: relative;
  width: 210px;
  height: 38px;
  border-radius: 10px;
  background: var(--bg-soft);
  display: flex;
  align-items: center;
}

.model-select {
  width: 100%;
  height: 100%;
  padding: 0 30px 0 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--ink-2);
  appearance: none;
  cursor: pointer;
}

.select-arrow {
  position: absolute;
  right: 10px;
  color: var(--ink-3);
  font-size: 14px;
  pointer-events: none;
}

.clear-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 14px;
  border-radius: 10px;
  background: var(--bg-soft);
  color: var(--ink-3);
  font-size: 13px;
}

.clear-btn:hover {
  color: var(--red);
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

.generate-hint {
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

@media (max-width: 1100px) {
  .left-column {
    width: 320px;
  }
}

@media (max-width: 860px) {
  .text-page {
    flex-direction: column;
  }
  .left-column {
    width: 100%;
    padding-top: 0;
  }
  .right-column {
    width: 100%;
    padding-top: 0;
  }
  .editor-card {
    height: 460px;
  }
}
</style>
