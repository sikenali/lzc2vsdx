const JSON_HEADERS = { 'Content-Type': 'application/json' }

async function request(path, options = {}) {
  const response = await fetch(path, options)
  const body = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(body.error || `请求失败 (${response.status})`)
  }
  return body
}

export function analyzeText(diagramType, text, model) {
  return request('/api/text/analyze', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ diagram_type: diagramType, text, model }),
  })
}

export function analyzeImage(file, demo = false) {
  const form = new FormData()
  form.append('image', file)
  return request(`/api/image/analyze${demo ? '?demo=1' : ''}`, {
    method: 'POST',
    body: form,
  })
}

export function createJob(payload) {
  return request('/api/jobs', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify(payload),
  })
}

export function getJob(id) {
  return request(`/api/jobs/${id}`)
}

export function cancelJob(id) {
  return request(`/api/jobs/${id}/cancel`, { method: 'POST' })
}

export function tweakJob(id, data) {
  return request(`/api/jobs/${id}/tweak`, {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ data }),
  })
}

export function downloadUrl(id) {
  return `/api/jobs/${id}/download`
}

export function subscribeJob(id, onUpdate, onEnd) {
  const source = new EventSource(`/api/jobs/${id}/events`)
  source.onmessage = (event) => {
    try {
      onUpdate(JSON.parse(event.data))
    } catch {
      // ignore malformed frame
    }
  }
  source.addEventListener('end', () => {
    source.close()
    onEnd && onEnd()
  })
  source.onerror = () => {
    source.close()
    onEnd && onEnd()
  }
  return () => source.close()
}
