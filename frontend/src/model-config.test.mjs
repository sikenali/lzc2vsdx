import test from 'node:test'
import assert from 'node:assert'
import { readFile } from 'node:fs/promises'

const read = (p) => readFile(new URL(p, import.meta.url), 'utf8')

test('preload 暴露模型配置读写（仅此 2 个方法）', async () => {
  const pre = await read('../../electron/preload.js')
  assert.match(pre, /contextBridge\.exposeInMainWorld\s*\(\s*['"]c2vsdx['"]/)
  assert.match(pre, /readModelConfig/)
  assert.match(pre, /writeModelConfig/)
  assert.doesNotMatch(pre, /fs\.|readFileSync|writeFileSync/)  // 不直接暴露 fs
})

test('main.js 注入 OPENVS_VISION_*/OPENVS_LLM_* 并监听 model-config IPC', async () => {
  const main = await read('../../electron/main.js')
  // 注入：6 个 OPENVS_* 映射
  for (const v of ['OPENVS_VISION_BASE_URL', 'OPENVS_VISION_API_KEY', 'OPENVS_VISION_MODEL',
                   'OPENVS_LLM_BASE_URL', 'OPENVS_LLM_API_KEY', 'OPENVS_LLM_MODEL']) {
    assert.match(main, new RegExp(v.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
  }
  // 非空判断才注入（不覆盖空字段）
  assert.match(main, /if\s*\(.*baseUrl|if\s*\(.*model|&&\s*[a-zA-Z]+\./)
  // IPC 监听
  assert.match(main, /ipcMain\.handle\s*\(\s*['"]model-config:read['"]/)
  assert.match(main, /ipcMain\.handle\s*\(\s*['"]model-config:write['"]/)
  // preload 挂载
  assert.match(main, /preload:\s*path\.join\s*\(\s*__dirname\s*,\s*['"]preload\.js['"]\s*\)/)
  // require ipcMain
  assert.match(main, /const\s*\{\s*[^}]*ipcMain[^}]*\}\s*=\s*require\s*\(\s*['"]electron['"]\s*\)/)
})
