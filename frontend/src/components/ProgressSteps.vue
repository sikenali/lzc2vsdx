<template>
  <div class="steps">
    <template v-for="(stage, index) in stages" :key="stage.key">
      <div class="step">
        <span class="step-circle" :class="stage.status">
          <i v-if="stage.status === 'done'" class="ri-check-line"></i>
          <span v-else>{{ index + 1 }}</span>
        </span>
        <span class="step-texts">
          <span class="step-title" :class="stage.status">{{ stage.label }}</span>
          <span class="step-detail">{{ detail(stage) }}</span>
        </span>
      </div>
      <div v-if="index < stages.length - 1" class="step-line">
        <span class="line-fill" :class="{ done: stage.status === 'done' }"></span>
      </div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  stages: { type: Array, required: true },
})

function detail(stage) {
  if (stage.status === 'done') return stage.detail?.startsWith('已完成') ? stage.detail : '已完成'
  if (stage.status === 'running') return stage.detail || '进行中'
  return '等待中'
}
</script>

<style scoped>
.steps {
  display: flex;
  align-items: center;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: none;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex: none;
}

.step-circle.done {
  background: var(--green);
  color: #fff;
  font-size: 16px;
}

.step-circle.running {
  background: var(--primary-fill);
  color: var(--primary-on);
}

.step-circle.pending {
  background: var(--bg-soft);
  color: var(--ink-5);
}

.step-texts {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.step-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--ink-2);
  white-space: nowrap;
}

.step-title.running {
  color: var(--red);
}

.step-title.pending {
  color: var(--ink-4);
  font-weight: 500;
}

.step-detail {
  font-size: 12px;
  color: var(--ink-4);
  white-space: nowrap;
}

.step-line {
  flex: 1;
  min-width: 24px;
  padding: 0 12px;
  display: flex;
  align-items: center;
}

.line-fill {
  width: 100%;
  height: 2px;
  background: var(--line);
  border-radius: 2px;
  display: block;
}

.line-fill.done {
  background: var(--green);
}

@media (max-width: 760px) {
  .steps {
    align-items: flex-start;
  }
  .step-line {
    min-width: 12px;
    padding: 0 6px;
    margin-top: 15px;
  }
  .step-title {
    font-size: 13px;
    white-space: normal;
  }
  .step-detail {
    font-size: 11px;
    white-space: normal;
  }
}
</style>
