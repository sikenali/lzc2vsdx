<template>
  <aside class="drawer">
    <div class="drawer-header">
      <div>
        <p class="drawer-title">在线微调</p>
        <p class="drawer-sub">修改节点文字与连线，保存后重新布局</p>
      </div>
      <button class="close-btn" @click="$emit('close')" aria-label="关闭"><i class="ri-close-line"></i></button>
    </div>

    <div class="drawer-body">
      <div class="group-head">
        <span>节点（{{ nodes.length }}）</span>
        <button class="mini-btn" @click="addNode"><i class="ri-add-line"></i>新增节点</button>
      </div>
      <div class="node-row" v-for="(node, index) in nodes" :key="node.id">
        <input v-model="node.label" class="mini-input" maxlength="20" placeholder="节点文字" />
        <select v-model="node.shape" class="mini-select">
          <option value="rectangle">矩形</option>
          <option value="diamond">菱形</option>
          <option value="stadium">胶囊</option>
        </select>
        <button class="icon-btn danger" @click="removeNode(index)" aria-label="删除节点">
          <i class="ri-delete-bin-line"></i>
        </button>
      </div>

      <div class="group-head edge-head">
        <span>连线（{{ edges.length }}）</span>
        <button class="mini-btn" @click="addEdge"><i class="ri-add-line"></i>新增连线</button>
      </div>
      <div class="edge-row" v-for="(edge, index) in edges" :key="index">
        <select v-model="edge.source" class="mini-select">
          <option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.label || n.id }}</option>
        </select>
        <span class="arrow">→</span>
        <select v-model="edge.target" class="mini-select">
          <option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.label || n.id }}</option>
        </select>
        <input v-model="edge.label" class="mini-input edge-label-input" maxlength="8" placeholder="标签" />
        <button class="icon-btn danger" @click="removeEdge(index)" aria-label="删除连线">
          <i class="ri-delete-bin-line"></i>
        </button>
      </div>
    </div>

    <div class="drawer-footer">
      <button class="btn-ghost" @click="$emit('close')">取消</button>
      <!-- A.11: handler 内守卫，不灰置 -->
      <button class="btn-primary save-btn" @click="save">
        <i class="ri-refresh-line"></i>
        <span>{{ saving ? '保存中…' : '保存并重新生成' }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { toast } from '../utils/toast'

const props = defineProps({ data: Object, saving: { type: Boolean, default: false } })
const emit  = defineEmits(['close', 'save'])

const nodes = ref((props.data.nodes || []).map(n => ({ ...n })))
const edges = ref((props.data.edges || []).map(e => ({ ...e })))
let customSeq = 0

function addNode() {
  customSeq += 1
  nodes.value.push({ id: `custom${Date.now()}_${customSeq}`, label: '新节点', shape: 'rectangle' })
}
function removeNode(i) {
  const [r] = nodes.value.splice(i, 1)
  edges.value = edges.value.filter(e => e.source !== r.id && e.target !== r.id)
}
function addEdge() {
  if (nodes.value.length < 2) return
  edges.value.push({ source: nodes.value[0].id, target: nodes.value[1].id, label: '' })
}
function removeEdge(i) { edges.value.splice(i, 1) }
function save() {
  if (props.saving) { toast('info', '进行中请稍候'); return }
  emit('save', { nodes: nodes.value, edges: edges.value })
}
</script>

<style scoped>
.drawer {
  position: fixed; top: 64px; right: 0; bottom: 48px;
  width: 420px; max-width: 92vw;
  background: rgba(255, 255, 255, 0.92);
  -webkit-backdrop-filter: blur(16px) saturate(160%);
  backdrop-filter: blur(16px) saturate(160%);
  border-left: 0.6px solid var(--line);
  box-shadow: var(--shadow-lg);
  z-index: 40; display: flex; flex-direction: column;
}

[data-theme="dark"] .drawer {
  background: rgba(15, 22, 35, 0.95);
  border-left-color: rgba(0, 212, 170, 0.12);
}

.drawer-header {
  padding: 16px 20px;
  display: flex; align-items: flex-start; justify-content: space-between;
  border-bottom: 0.6px solid var(--line);
}

.drawer-title {
  font-size: 16px; font-weight: 600; color: var(--ink);
  font-family: var(--font-display);
}
.drawer-sub { margin-top: 3px; font-size: 12px; color: var(--ink-4); }

.close-btn {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--bg-soft); color: var(--ink-3); font-size: 15px;
  border: none; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
  transition: background var(--t-fast) var(--ease-spring), color var(--t-fast) ease;
}
.close-btn:hover { background: rgba(0, 212, 170, 0.12); color: var(--tech-cyan); }

.drawer-body { flex: 1; overflow-y: auto; padding: 14px 20px; }

.group-head {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 12px; font-weight: 600; color: var(--ink-2); margin-bottom: 8px;
  font-family: var(--font-display);
}
.edge-head { margin-top: 18px; }

.mini-btn {
  display: inline-flex; align-items: center; gap: 4px; font-size: 11px;
  color: var(--tech-cyan); border: none; background: transparent; cursor: pointer;
  transition: opacity var(--t-fast) ease;
}
.mini-btn:hover { opacity: 0.75; }

.node-row, .edge-row {
  display: flex; align-items: center; gap: 6px; margin-bottom: 6px;
}

.mini-input, .mini-select {
  height: 32px; border-radius: var(--radius-sm);
  border: 0.6px solid var(--line); background: var(--bg-soft);
  padding: 0 8px; font-size: 12px; min-width: 0; color: var(--ink-2);
  transition: border-color var(--t-fast) ease, box-shadow var(--t-fast) ease;
}
.mini-input:focus, .mini-select:focus {
  border-color: var(--tech-cyan);
  box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.15);
  outline: none;
}
.mini-input { flex: 1; }
.mini-select { width: 80px; }
.edge-label-input { flex: none; width: 68px; }

.arrow { color: var(--ink-4); font-size: 12px; }

.icon-btn {
  width: 28px; height: 28px; border-radius: var(--radius-sm);
  background: var(--bg-soft); color: var(--ink-4); border: none;
  cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
  font-size: 13px;
  transition: background var(--t-fast) ease, color var(--t-fast) ease;
}
.icon-btn.danger:hover { background: rgba(255, 77, 109, 0.1); color: var(--tech-coral); }

.drawer-footer {
  padding: 12px 20px;
  border-top: 0.6px solid var(--line);
  display: flex; justify-content: flex-end; gap: 8px;
}

.save-btn { height: 38px; padding: 0 18px; font-size: 13px; }
</style>