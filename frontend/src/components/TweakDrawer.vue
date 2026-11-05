<template>
  <aside class="drawer">
    <div class="drawer-header">
      <div>
        <p class="drawer-title">在线微调</p>
        <p class="drawer-sub">修改节点文字与连线，保存后重新布局</p>
      </div>
      <button class="close-btn" @click="$emit('close')"><i class="ri-close-line"></i></button>
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
        <button class="icon-btn danger" @click="removeNode(index)"><i class="ri-delete-bin-line"></i></button>
      </div>

      <div class="group-head edge-head">
        <span>连线（{{ edges.length }}）</span>
        <button class="mini-btn" @click="addEdge"><i class="ri-add-line"></i>新增连线</button>
      </div>
      <div class="edge-row" v-for="(edge, index) in edges" :key="index">
        <select v-model="edge.source" class="mini-select">
          <option v-for="node in nodes" :key="node.id" :value="node.id">{{ node.label || node.id }}</option>
        </select>
        <span class="arrow">→</span>
        <select v-model="edge.target" class="mini-select">
          <option v-for="node in nodes" :key="node.id" :value="node.id">{{ node.label || node.id }}</option>
        </select>
        <input v-model="edge.label" class="mini-input edge-label-input" maxlength="8" placeholder="标签" />
        <button class="icon-btn danger" @click="removeEdge(index)"><i class="ri-delete-bin-line"></i></button>
      </div>
    </div>

    <div class="drawer-footer">
      <button class="btn-ghost" @click="$emit('close')">取消</button>
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

const props = defineProps({
  data: { type: Object, required: true },
  saving: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'save'])

const nodes = ref((props.data.nodes || []).map((n) => ({ ...n })))
const edges = ref((props.data.edges || []).map((e) => ({ ...e })))
let customSeq = 0

function addNode() {
  customSeq += 1
  nodes.value.push({
    id: `custom${Date.now()}_${customSeq}`,
    label: '新节点',
    shape: 'rectangle',
  })
}

function removeNode(index) {
  const [removed] = nodes.value.splice(index, 1)
  edges.value = edges.value.filter((e) => e.source !== removed.id && e.target !== removed.id)
}

function addEdge() {
  if (nodes.value.length < 2) return
  edges.value.push({ source: nodes.value[0].id, target: nodes.value[1].id, label: '' })
}

function removeEdge(index) {
  edges.value.splice(index, 1)
}

function save() {
  if (props.saving) {
    toast('info', '进行中请稍候')
    return
  }
  emit('save', { nodes: nodes.value, edges: edges.value })
}
</script>

<style scoped>
.drawer {
  position: fixed;
  top: 72px;
  right: 0;
  bottom: 58px;
  width: 460px;
  max-width: 92vw;
  background: #fff;
  border-left: 0.7px solid var(--line);
  box-shadow: -12px 0 32px rgba(31, 29, 26, 0.08);
  z-index: 40;
  display: flex;
  flex-direction: column;
}

.drawer-header {
  padding: 20px 24px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  border-bottom: 1px solid var(--line-soft);
}

.drawer-title {
  font-size: 17px;
  font-weight: 600;
}

.drawer-sub {
  margin-top: 4px;
  font-size: 12px;
  color: var(--ink-4);
}

.close-btn {
  width: 30px;
  height: 30px;
  border-radius: 9999px;
  background: var(--bg-soft);
  color: var(--ink-3);
  font-size: 16px;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 18px 24px;
}

.group-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-2);
  margin-bottom: 10px;
}

.edge-head {
  margin-top: 22px;
}

.mini-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--red);
}

.node-row,
.edge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.mini-input,
.mini-select {
  height: 34px;
  border-radius: 8px;
  border: 0.7px solid var(--line);
  background: var(--bg-footer);
  padding: 0 10px;
  font-size: 13px;
  min-width: 0;
}

.mini-input {
  flex: 1;
}

.mini-select {
  width: 86px;
}

.edge-label-input {
  flex: none;
  width: 74px;
}

.arrow {
  color: var(--ink-4);
  font-size: 13px;
}

.icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: var(--bg-soft);
  color: var(--ink-4);
  flex: none;
}

.icon-btn.danger:hover {
  color: var(--red);
}

.drawer-footer {
  padding: 14px 24px;
  border-top: 1px solid var(--line-soft);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.save-btn {
  height: 44px;
  padding: 0 20px;
  font-size: 14px;
}
</style>
