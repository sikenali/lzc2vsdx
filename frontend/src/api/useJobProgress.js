import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cancelJob, getJob, subscribeJob } from '../api/client'
import { loadSession, saveSession } from '../api/store'

export function useJobProgress(mode) {
  const route = useRoute()
  const router = useRouter()
  const jobId = String(route.params.id)
  const job = ref(loadSession(jobId) || null)
  const error = ref('')
  let unsubscribe = null
  let pollTimer = null
  let redirected = false

  const progress = computed(() => job.value?.progress ?? 0)
  const remaining = computed(() => {
    if (!job.value || job.value.status !== 'running') return 0
    return Math.max(1, Math.round((100 - progress.value) / 9))
  })
  const stats = computed(() => job.value?.stats || { nodes: 0, edges: 0, labels: 0 })
  const stages = computed(() => job.value?.stages || [
    { key: 'analyze', label: mode === 'image' ? '图片解析' : '文本解析', status: 'pending', detail: '' },
    { key: 'structure', label: mode === 'image' ? '结构识别' : '语义理解与结构抽取', status: 'pending', detail: '' },
    { key: 'render', label: 'VSDX 生成', status: 'pending', detail: '' },
  ])

  function finish(data) {
    job.value = data
    if (data.status === 'error') {
      error.value = data.error || '生成失败，请检查后端环境或输入数据'
    } else if (data.status === 'cancelled') {
      error.value = '生成已取消'
    }
    if (data.status === 'done' && !redirected) {
      redirected = true
      saveSession(jobId, { ...loadSession(jobId), ...data })
      setTimeout(() => router.replace(`/result/${jobId}`), 450)
    }
  }

  function startPolling() {
    if (pollTimer) return
    pollTimer = setInterval(async () => {
      try {
        const data = await getJob(jobId)
        finish(data)
        if (['done', 'error', 'cancelled'].includes(data.status)) {
          clearInterval(pollTimer)
          pollTimer = null
        }
      } catch {
        // 下一轮继续
      }
    }, 1000)
  }

  function start() {
    getJob(jobId).then(finish).catch((err) => {
      if (!job.value) error.value = err.message
    })
    unsubscribe = subscribeJob(jobId, finish, () => {
      // SSE 提前断开（网络/超时）时退回轮询，避免页面永远停在进度中
      const status = job.value?.status
      if (!['done', 'error', 'cancelled'].includes(status)) startPolling()
    })
  }

  async function cancel() {
    try {
      await cancelJob(jobId)
    } catch {
      // job may already be finished
    }
    unsubscribe && unsubscribe()
    router.push(mode === 'image' ? '/image' : '/')
  }

  onMounted(start)
  onBeforeUnmount(() => {
    unsubscribe && unsubscribe()
    if (pollTimer) clearInterval(pollTimer)
  })

  return { job, jobId, error, progress, remaining, stats, stages, cancel }
}
