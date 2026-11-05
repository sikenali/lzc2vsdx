<template>
  <div
    ref="wrapEl"
    class="diagram-wrap"
    :class="{ dragging }"
    @mousedown="startDrag"
    @mousemove="onDrag"
    @mouseup="endDrag"
    @mouseleave="endDrag"
  >
    <svg
      :viewBox="`0 0 ${preview.width} ${preview.height}`"
      :style="{ width: svgWidth + 'px' }"
      class="diagram-svg"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#B0A79A" />
        </marker>
      </defs>

      <g v-if="preview.lifelines">
        <line
          v-for="line in preview.lifelines"
          :key="line.id"
          :x1="line.x"
          :y1="line.y1"
          :x2="line.x"
          :y2="line.y2"
          stroke="#D9D2C2"
          stroke-width="0.03"
          stroke-dasharray="0.12 0.1"
        />
      </g>

      <g v-for="(frag, i) in preview.fragments || []" :key="'f' + i">
        <rect
          :x="frag.x1"
          :y="frag.y1"
          :width="frag.x2 - frag.x1"
          :height="frag.y2 - frag.y1"
          fill="none"
          stroke="#D9D2C2"
          stroke-width="0.04"
          stroke-dasharray="0.14 0.12"
        />
        <text :x="frag.x1 + 0.15" :y="frag.y1 + 0.22" class="frag-label">{{ frag.label || frag.type }}</text>
      </g>

      <g v-for="(edge, i) in preview.edges" :key="'e' + i">
        <polyline
          :points="(edge.points || []).map((p) => p.join(',')).join(' ')"
          fill="none"
          :stroke="edge.color || (edge.dashed ? '#C9C2B4' : '#B0A79A')"
          :stroke-width="edge.width ? edge.width / 72 : 0.04"
          :stroke-dasharray="edge.dashed ? '0.14 0.12' : ''"
          marker-end="url(#arrow)"
        />
        <text
          v-if="edge.label"
          :x="labelPoint(edge).x"
          :y="labelPoint(edge).y - 0.12"
          class="edge-label"
          text-anchor="middle"
        >{{ edge.label }}</text>
      </g>

      <g v-for="node in preview.nodes" :key="node.id">
        <template v-if="node.shape === 'textbox'">
          <!-- 无边框浮动文字 -->
        </template>
        <template v-else-if="node.shape === 'ellipse'">
          <ellipse
            :cx="node.x"
            :cy="node.y"
            :rx="node.w / 2"
            :ry="node.h / 2"
            :fill="node.fill || '#FFFFFF'"
            :stroke="node.border || '#D9D2C2'"
            stroke-width="0.05"
          />
        </template>
        <template v-else-if="node.shape === 'hexagon'">
          <polygon
            :points="hexPoints(node)"
            :fill="node.fill || '#FFFFFF'"
            :stroke="node.border || '#D9D2C2'"
            stroke-width="0.05"
          />
        </template>
        <template v-else-if="node.shape === 'parallelogram'">
          <polygon
            :points="parallelogramPoints(node)"
            :fill="node.fill || '#FFFFFF'"
            :stroke="node.border || '#D9D2C2'"
            stroke-width="0.05"
          />
        </template>
        <template v-else-if="node.shape === 'document'">
          <path
            :d="documentPath(node)"
            :fill="node.fill || '#FFFFFF'"
            :stroke="node.border || '#D9D2C2'"
            stroke-width="0.05"
          />
        </template>
        <template v-else-if="node.shape === 'storage'">
          <rect
            :x="node.x - node.w / 2"
            :y="node.y - node.h / 2"
            :width="node.w"
            :height="node.h"
            :rx="node.w * 0.12"
            :fill="node.fill || '#FFFFFF'"
            :stroke="node.border || '#D9D2C2'"
            stroke-width="0.05"
          />
        </template>
        <template v-else-if="node.shape === 'diamond'">
          <polygon
            :points="diamondPoints(node)"
            :fill="node.fill || '#FBE9E7'"
            :stroke="node.border || '#C0392B'"
            stroke-width="0.05"
          />
        </template>
        <template v-else-if="node.shape === 'stadium' || node.shape === 'rounded' || node.shape === 'rounded_rectangle'">
          <rect
            :x="node.x - node.w / 2"
            :y="node.y - node.h / 2"
            :width="node.w"
            :height="node.h"
            :rx="Math.min(node.h / 2, 0.3)"
            :fill="node.fill || '#FFFFFF'"
            :stroke="node.border || '#D9D2C2'"
            stroke-width="0.05"
          />
        </template>
        <template v-else>
          <rect
            :x="node.x - node.w / 2"
            :y="node.y - node.h / 2"
            :width="node.w"
            :height="node.h"
            :rx="node.shape === 'layer' || node.shape === 'lane' ? 0.1 : 0"
            :fill="node.fill || fillFor(node)"
            :stroke="node.border || borderFor(node)"
            stroke-width="0.05"
          />
        </template>

        <text
          v-if="node.label"
          :x="node.x"
          :y="node.y - textOffset(node)"
          class="node-label"
          :fill="node.text_color || textFor(node)"
          text-anchor="middle"
        >
          <tspan v-for="(line, li) in wrap(node.label, node.w)" :key="li" :x="node.x" :dy="li === 0 ? 0 : 0.26">{{ line }}</tspan>
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  preview: { type: Object, required: true },
  zoom: { type: Number, default: 100 },
})

const wrapEl = ref(null)
const wrapWidth = ref(1000)
let observer = null
const dragging = ref(false)
let dragStart = { x: 0, y: 0, left: 0, top: 0 }

function startDrag(event) {
  const el = wrapEl.value
  if (!el) return
  dragging.value = true
  dragStart = { x: event.clientX, y: event.clientY, left: el.scrollLeft, top: el.scrollTop }
}

function onDrag(event) {
  if (!dragging.value) return
  const el = wrapEl.value
  if (!el) return
  el.scrollLeft = dragStart.left - (event.clientX - dragStart.x)
  el.scrollTop = dragStart.top - (event.clientY - dragStart.y)
}

function endDrag() {
  dragging.value = false
}

const fitScale = computed(() => {
  const w = Math.max(320, wrapWidth.value - 32)
  const h = 340
  return Math.min(w / props.preview.width, h / props.preview.height)
})

const svgWidth = computed(() => Math.max(240, props.preview.width * fitScale.value * (props.zoom / 100)))

onMounted(() => {
  if (typeof ResizeObserver !== 'undefined' && wrapEl.value) {
    observer = new ResizeObserver((entries) => {
      for (const entry of entries) wrapWidth.value = entry.contentRect.width
    })
    observer.observe(wrapEl.value)
  }
  if (wrapEl.value) wrapWidth.value = wrapEl.value.clientWidth
})

onBeforeUnmount(() => observer?.disconnect())

watch(() => props.preview, () => {
  if (wrapEl.value) wrapWidth.value = wrapEl.value.clientWidth
})

function diamondPoints(node) {
  const { x, y, w, h } = node
  return `${x},${y - h / 2} ${x + w / 2},${y} ${x},${y + h / 2} ${x - w / 2},${y}`
}

function hexPoints(node) {
  const { x, y, w, h } = node
  const inset = w * 0.16
  return `${x - w / 2 + inset},${y - h / 2} ${x + w / 2 - inset},${y - h / 2} ${x + w / 2},${y} ${x + w / 2 - inset},${y + h / 2} ${x - w / 2 + inset},${y + h / 2} ${x - w / 2},${y}`
}

function parallelogramPoints(node) {
  const { x, y, w, h } = node
  const skew = w * 0.18
  return `${x - w / 2 + skew},${y - h / 2} ${x + w / 2},${y - h / 2} ${x + w / 2 - skew},${y + h / 2} ${x - w / 2},${y + h / 2}`
}

function documentPath(node) {
  const { x, y, w, h } = node
  const left = x - w / 2
  const right = x + w / 2
  const top = y - h / 2
  const bottom = y + h / 2
  const wave = h * 0.12
  return `M ${left} ${top} L ${right} ${top} L ${right} ${bottom - wave} ` +
    `C ${right - w * 0.25} ${bottom + wave} ${left + w * 0.25} ${bottom - wave * 2} ${left} ${bottom} Z`
}

function labelPoint(edge) {
  const pts = edge.points || []
  if (!pts.length) return { x: 0, y: 0 }
  if (pts.length === 2) {
    return { x: (pts[0][0] + pts[1][0]) / 2, y: (pts[0][1] + pts[1][1]) / 2 }
  }
  const a = pts[Math.floor((pts.length - 1) / 2)]
  const b = pts[Math.floor(pts.length / 2)]
  return { x: (a[0] + b[0]) / 2, y: (a[1] + b[1]) / 2 }
}

function wrap(label, width) {
  const max = Math.max(6, Math.floor(width * 7))
  const lines = []
  for (const raw of String(label || '').split('\n')) {
    const chars = [...raw]
    if (chars.length <= max) {
      lines.push(raw)
    } else {
      for (let i = 0; i < chars.length; i += max) lines.push(chars.slice(i, i + max).join(''))
    }
  }
  return lines.slice(0, 6)
}

function textOffset(node) {
  const lines = wrap(node.label, node.w).length
  return 0.07 + Math.max(0, lines - 1) * 0.13
}

function fillFor(node) {
  const label = node.label || ''
  if (label.includes('成功')) return '#E4F0EA'
  if (label.includes('错误') || label.includes('失败')) return '#FEF5E7'
  if (node.shape === 'layer') return '#F7F3EA'
  if (node.shape === 'lane') return '#FCFBF8'
  return '#FFFFFF'
}

function borderFor(node) {
  const label = node.label || ''
  if (label.includes('成功')) return '#4E9B7A'
  if (label.includes('错误') || label.includes('失败')) return '#F39C12'
  if (node.shape === 'layer') return '#E5DFD3'
  return '#D9D2C2'
}

function textFor(node) {
  const label = node.label || ''
  if (label.includes('成功')) return '#2F6E55'
  if (label.includes('错误') || label.includes('失败')) return '#9A6B10'
  return '#3A3A3A'
}
</script>

<style scoped>
.diagram-wrap {
  width: 100%;
  height: 340px;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: grab;
}

.diagram-wrap.dragging {
  cursor: grabbing;
  user-select: none;
}

.diagram-svg {
  display: block;
  height: auto;
  max-width: none;
}

.node-label {
  font-family: var(--font);
  font-size: 0.18px;
  paint-order: stroke;
}

.edge-label {
  font-family: var(--font);
  font-size: 0.16px;
  fill: #8a8578;
}

.frag-label {
  font-family: var(--font);
  font-size: 0.15px;
  fill: #8a8578;
}
</style>
