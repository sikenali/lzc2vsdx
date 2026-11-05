<template>
  <div class="skeleton">
    <svg v-if="mode === 'image'" viewBox="0 0 700 330" class="skeleton-svg">
      <rect x="110" y="40" width="160" height="56" rx="2" fill="#F7F3EA" stroke="#E5DFD3" />
      <rect x="470" y="40" width="160" height="56" rx="2" fill="#F7F3EA" stroke="#E5DFD3" />
      <line x1="290" y1="68" x2="470" y2="68" stroke="#E5DFD3" stroke-width="2" stroke-dasharray="6 5" />
      <line x1="390" y1="96" x2="390" y2="150" stroke="#E5DFD3" stroke-width="2" stroke-dasharray="6 5" />
      <rect x="290" y="150" width="200" height="56" rx="2" fill="#FBE9E7" stroke="#E3B7B1" stroke-width="1.2" />
      <rect x="180" y="206" width="160" height="56" rx="2" fill="#F7F3EA" stroke="#E5DFD3" />
      <rect x="470" y="206" width="160" height="56" rx="2" fill="#F7F3EA" stroke="#E5DFD3" />
      <path d="M390 206 L390 230 L260 230 L260 262" stroke="#E5DFD3" stroke-width="2" stroke-dasharray="6 5" fill="none" />
      <path d="M390 206 L390 230 L550 230 L550 262" stroke="#E5DFD3" stroke-width="2" stroke-dasharray="6 5" fill="none" />
      <line x1="130" y1="68" x2="250" y2="68" stroke="#E8E2D6" stroke-width="8" stroke-linecap="round" />
      <line x1="490" y1="68" x2="610" y2="68" stroke="#E8E2D6" stroke-width="8" stroke-linecap="round" />
      <line x1="320" y1="168" x2="460" y2="168" stroke="#F3CFCA" stroke-width="8" stroke-linecap="round" />
      <line x1="210" y1="224" x2="310" y2="224" stroke="#E8E2D6" stroke-width="8" stroke-linecap="round" />
      <line x1="500" y1="224" x2="600" y2="224" stroke="#E8E2D6" stroke-width="8" stroke-linecap="round" />
      <text x="190" y="73" class="sk-label">开始</text>
      <text x="550" y="73" class="sk-label">输入手机号</text>
      <text x="390" y="183" class="sk-label active">校验验证码</text>
      <text x="260" y="239" class="sk-label">提示错误</text>
      <text x="550" y="239" class="sk-label">登录成功</text>
      <text x="350" y="20" class="sk-note">AI 正在推断图形层级与连接关系</text>
    </svg>

    <svg v-else viewBox="0 0 760 330" class="skeleton-svg">
      <rect x="90" y="70" width="290" height="140" rx="2" fill="#F7F3EA" stroke="#E5DFD3" />
      <line x1="115" y1="95" x2="330" y2="95" stroke="#E8E2D6" stroke-width="8" stroke-linecap="round" />
      <line x1="115" y1="118" x2="355" y2="118" stroke="#E8E2D6" stroke-width="8" stroke-linecap="round" />
      <line x1="115" y1="141" x2="275" y2="141" stroke="#E8E2D6" stroke-width="8" stroke-linecap="round" />
      <line x1="115" y1="164" x2="320" y2="164" stroke="#E8E2D6" stroke-width="8" stroke-linecap="round" />
      <path d="M390 140 L450 140" stroke="#C9C2B4" stroke-width="2" stroke-dasharray="5 4" />
      <path d="M450 140 L458 134 M450 140 L458 146" stroke="#C9C2B4" stroke-width="2" />
      <text x="410" y="128" class="sk-note">AI 抽取</text>
      <rect x="470" y="95" width="130" height="56" rx="2" fill="#FFFFFF" stroke="#D9D2C2" />
      <rect x="620" y="95" width="130" height="56" rx="2" fill="#FFFFFF" stroke="#D9D2C2" />
      <line x1="600" y1="123" x2="620" y2="123" stroke="#D9D2C2" stroke-width="2" />
      <text x="535" y="127" class="sk-label">输入手机号</text>
      <text x="685" y="127" class="sk-label">获取验证码</text>
      <path d="M535 151 L535 172 L575 172 L575 195" stroke="#E5DFD3" stroke-width="2" stroke-dasharray="6 5" fill="none" />
      <path d="M685 151 L685 172 L625 172 L625 195" stroke="#E5DFD3" stroke-width="2" stroke-dasharray="6 5" fill="none" />
      <rect x="480" y="195" width="190" height="56" rx="2" fill="#FBE9E7" stroke="#E3B7B1" stroke-width="1.2" />
      <text x="575" y="227" class="sk-label active">校验验证码</text>
      <text x="235" y="45" class="sk-note">需求描述文本 · 已解析</text>
      <text x="380" y="290" class="sk-note">AI 正在从需求文本中推断节点层级与连接关系</text>
    </svg>
  </div>
</template>

<script setup>
defineProps({
  mode: { type: String, default: 'image' },
})
</script>

<style scoped>
.skeleton {
  width: 100%;
  min-height: 340px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 0;
}

.skeleton-svg {
  width: 100%;
  max-width: 720px;
  height: auto;
}

.sk-label {
  font-family: var(--font);
  font-size: 13px;
  fill: #c9c2b4;
}

.sk-label.active {
  fill: #c08c86;
}

.sk-note {
  font-family: var(--font);
  font-size: 12px;
  fill: #b6c0ce;
  text-anchor: middle;
}

.skeleton-svg rect,
.skeleton-svg line,
.skeleton-svg path {
  animation: pulse 1.8s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.72;
  }
}
</style>
