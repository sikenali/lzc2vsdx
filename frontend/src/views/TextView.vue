<template>
  <div class="text-page">
    <div class="left-column">
      <div class="type-header">
        <div class="section-title-row">
          <span class="title-bar"></span>
          <span class="title-text">选择图表类型</span>
          <span class="title-desc">单选，切换即重新生成</span>
        </div>
        <div class="selected-count"><span>已选</span><strong>1</strong><span>项</span></div>
      </div>

      <div class="type-list">
        <TypeCard v-for="item in types" :key="item.key" :item="item" :active="selected === item.key" @select="selected = $event" />
      </div>
    </div>

    <div class="right-column">
      <section class="editor-card card">
        <div class="editor-header">
          <div class="editor-title"><i class="ri-file-text-line"></i><span>需求描述文本</span></div>
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
          <textarea v-else ref="textarea" v-model="text" class="text-input" spellcheck="false" @blur="editing = false"></textarea>
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
          <button class="clear-btn" @click="clearText"><i class="ri-delete-bin-line"></i><span>清空</span></button>
        </div>
      </section>

      <div class="generate-area">
        <!-- A.11: handler 内守卫，不灰置 -->
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

/* §2.3.2 brand 色板对应 6 类图表 */
const types = [
  { key: 'flowchart',    title: '流程图',  desc: '节点流转与分支',  icon: 'ri-flow-chart',         iconColor: '#FFB347', iconBg: 'rgba(255,179,71,0.1)' },
  { key: 'sequence',     title: '时序图',  desc: '参与者消息交互',  icon: 'ri-time-line',          iconColor: '#4A9EFF', iconBg: 'rgba(74,158,255,0.1)' },
  { key: 'composition',  title: '组成图',  desc: '模块构成拆解',    icon: 'ri-stack-line',         iconColor: '#00D4AA', iconBg: 'rgba(0,212,170,0.1)' },
  { key: 'component',    title: '关系图',  desc: '实体关联映射',    icon: 'ri-links-line',         iconColor: '#00A878', iconBg: 'rgba(0,168,120,0.1)' },
  { key: 'architecture', title: '架构图',  desc: '分层系统架构',    icon: 'ri-building-2-line',    iconColor: '#94A3B8', iconBg: 'rgba(148,163,184,0.1)' },
  { key: 'swimlane',     title: '泳道图',  desc: '跨角色流程泳道',  icon: 'ri-layout-column-line', iconColor: '#FF4D6D', iconBg: 'rgba(255,77,109,0.1)' },
]

const SAMPLE = `用户登录流程
用户打开 App 后进入登录页，页面展示手机号输入框、验证码输入框以及「登录」按钮，并在底部提供「遇到问题？」帮助入口。
用户在 60 秒内填写验证码并点击「登录」，前端完成非空校验后调用登录接口。
登录接口依次校验：若手机号未注册，返回「账号不存在」并引导注册；若验证码错误，返回剩余重试次数（最多 5 次）；以上校验均通过则签发 Token。
Token 写入本地安全缓存后，系统并行请求用户信息接口与权限接口，完成后跳转至首页。`

const text     = ref(SAMPLE)
const selected = ref('flowchart')
const model    = ref('c2vsdx-graph-v2')
const editing  = ref(false)
const loading  = ref(false)
const textarea = ref(null)

onMounted(() => {
  const last = loadLastInput()
  if (last?.mode === 'text' && last.text) {
    text.value = last.text
    selected.value = last.diagram_type || 'flowchart'
  }
})

const paragraphs     = computed(() => text.value.split('\n').map(p => p.trim()).filter(Boolean))
const charCount      = computed(() => text.value.replace(/\s/g, '').length)
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
  /* A.11: handler 内守卫 */
  if (loading.value)      { toast('info', '进行中请稍候'); return }
  if (!text.value.trim()) { toast('warning', '请先输入需求描述'); return }
  loading.value = true
  try {
    const parsed = await analyzeText(selected.value, text.value, model.value)
    saveLastInput({ mode: 'text', diagram_type: selected.value, text: text.value })
    const job = await createJob({
      mode: 'text', diagram_type: selected.value,
      data: parsed.data, title: parsed.title, stats: parsed.stats,
    })
    saveSession(job.id, { ...job, diagram_type: selected.value, data: parsed.data })
    router.push(`/text/progress/${job.id}`)
  } catch (e) { toast('error', e.message) }
  finally { loading.value = false }
}
</script>

<style scoped>
.text-page { display: flex; align-items: flex-start; gap: 16px; }
.left-column  { width: 320px; flex: none; padding-top: 16px; }
.right-column { flex: 1; min-width: 0; padding-top: 16px; }

.type-header { display: flex; align-items: center; justify-content: space-between; }
.selected-count { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--ink-4); }
.selected-count strong { color: var(--tech-cyan); font-weight: 600; font-family: var(--font-mono); }

.type-list { margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }

.editor-card { height: 480px; display: flex; flex-direction: column; overflow: hidden; }
.editor-header {
  height: 46px; flex: none;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px;
}
.editor-title {
  display: flex; align-items: center; gap: 6px;
  font-size: 14px; font-weight: 600;
  font-family: var(--font-display);
}
.editor-title .ri { color: var(--tech-cyan); font-size: 16px; }
.editor-count { font-size: 12px; color: var(--ink-4); font-family: var(--font-mono); }

.editor-body { flex: 1; min-height: 0; padding: 16px 18px; overflow-y: auto; cursor: text; }
.text-title-line  { font-size: 14px; font-weight: 600; line-height: 1.2; color: var(--ink); margin-bottom: 10px; font-family: var(--font-display); }
.text-paragraph   { font-size: 13px; line-height: 1.36; color: var(--ink-2); margin-bottom: 6px; }
.text-placeholder { font-size: 13px; line-height: 1.36; color: var(--ink-5); margin-top: 6px; }

/* §10.2 input focus：电光青边框 + 外发光 */
.text-input {
  width: 100%; height: 100%; min-height: 340px; resize: none;
  font-size: 13px; line-height: 1.45; color: var(--ink-2); background: transparent;
}
.text-input:focus {
  outline: none;
  box-shadow: inset 0 0 0 1px var(--tech-cyan), 0 0 0 3px rgba(0, 212, 170, 0.15);
}

.model-select:focus {
  outline: none;
  border-color: var(--tech-cyan);
  box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.3);
  border-radius: var(--radius-sm);
}

.editor-divider { height: 1px; background: var(--line-soft); flex: none; }
.editor-footer {
  height: 46px; flex: none;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px; background: var(--bg-footer);
}

.model-select-wrap {
  position: relative; width: 190px; height: 34px;
  border-radius: var(--radius-sm); background: var(--bg-soft);
  display: flex; align-items: center;
  border: 0.6px solid var(--line); overflow: hidden;
}
.model-select {
  width: 100%; height: 100%; padding: 0 28px 0 10px;
  font-size: 12px; font-weight: 500; color: var(--ink-2);
  appearance: none; cursor: pointer; background: transparent;
  font-family: var(--font-mono);
}
.select-arrow {
  position: absolute; right: 8px; color: var(--ink-3); font-size: 13px; pointer-events: none;
}

.clear-btn {
  display: inline-flex; align-items: center; gap: 5px;
  height: 34px; padding: 0 12px;
  border-radius: var(--radius-sm); background: var(--bg-soft); color: var(--ink-3);
  font-size: 12px; border: 0.6px solid var(--line);
  transition: background var(--t-fast) ease, color var(--t-fast) ease;
}
.clear-btn:hover { color: var(--tech-cyan); background: rgba(0, 212, 170, 0.08); }

.generate-area { margin-top: 18px; display: flex; flex-direction: column; align-items: center; }
.generate-btn  { min-width: 200px; }
.generate-hint { margin-top: 10px; text-align: center; }

.spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1000px) { .left-column { width: 280px; } }
@media (max-width: 760px) {
  .text-page { flex-direction: column; }
  .left-column, .right-column { width: 100%; padding-top: 0; }
  .editor-card { height: 400px; }
}
</style>