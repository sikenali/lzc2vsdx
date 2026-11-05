const PREFIX = 'c2vsdx:'

export function saveSession(id, payload) {
  sessionStorage.setItem(`${PREFIX}${id}`, JSON.stringify(payload))
}

export function loadSession(id) {
  try {
    return JSON.parse(sessionStorage.getItem(`${PREFIX}${id}`) || 'null')
  } catch {
    return null
  }
}

export function saveLastInput(payload) {
  sessionStorage.setItem(`${PREFIX}last`, JSON.stringify(payload))
}

export function loadLastInput() {
  try {
    return JSON.parse(sessionStorage.getItem(`${PREFIX}last`) || 'null')
  } catch {
    return null
  }
}
