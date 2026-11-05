import test from 'node:test'
import assert from 'node:assert'
import { readFile } from 'node:fs/promises'

const read = (p) => readFile(new URL(p, import.meta.url), 'utf8')

test('toast 事件契约为 {type,message} 且 §9 顶部居中', async () => {
  const app = await read('./App.vue')
  // §9 位置：顶部居中
  assert.match(app, /top:\s*20px/)
  assert.match(app, /left:\s*50%/)
  assert.match(app, /z-index:\s*10000/)
  // 事件契约：读取 event.detail 并构建 {type,message}
  assert.match(app, /event\.detail/)
  assert.match(app, /toast\.value\s*=\s*\{\s*(type|message)[^}]*,\s*(type|message)/)
  // 模板用 toast.message / toast.type（不再裸 toast 字符串）
  assert.match(app, /toast\.message|toast\?\.message|toast\.type/)
  // §9 类型色条
  assert.match(app, /toast-bar|--green|--red|--orange|--blue/)
  // 统一助手：utils/toast.js 导出 toast(type, message) dispatch {type,message}
  const util = await read('./utils/toast.js')
  assert.match(util, /export\s+function\s+toast/)
  assert.match(util, /detail:\s*\{\s*type,\s*message\s*\}/)
})

test('各调用点使用统一 toast 助手并传类型', async () => {
  for (const f of [
    './views/TextView.vue',
    './views/ImageView.vue',
    './views/ResultView.vue',
    './components/AppFooter.vue',
    './components/settings/ThemeSettingsView.vue',
  ]) {
    const src = await read(f)
    assert.match(src, /import\s+\{\s*toast\s*\}\s+from\s+['"].*utils\/toast['"]/, `${f} 应导入统一 toast`)
    assert.doesNotMatch(src, /function\s+toast\(/, `${f} 不应再定义本地 toast`)
  }
})

test('tokens 提供 primary-fill/on 与体系圆角', async () => {
  const css = await read('./styles/tokens.css')
  assert.match(css, /--primary-fill:/)
  assert.match(css, /--primary-on:\s*#fff/i)
  assert.match(css, /\[data-theme="dark"\][\s\S]*--primary-fill:/)
  assert.match(css, /--radius-card:\s*14px/)
})

test('实底填充改用 primary-fill/on，硬编码色入 token', async () => {
  const base = await read('./styles/base.css')
  // .btn-primary 实底用 fill/on
  assert.match(base, /\.btn-primary\s*\{[\s\S]*background:\s*var\(--primary-fill\)/)
  assert.match(base, /\.btn-primary\s*\{[\s\S]*color:\s*var\(--primary-on\)/)
  // .btn-ghost 不再硬编码 #fff
  assert.match(base, /\.btn-ghost\s*\{[\s\S]*background:\s*var\(--bg-card\)/)
  assert.doesNotMatch(base, /\.btn-primary:disabled/)
  const result = await read('./views/ResultView.vue')
  assert.match(result, /\.stat-card\.red\s*\{[\s\S]*color:\s*var\(--red\)/)
  assert.doesNotMatch(result, /\.soft-action\s*\{[\s\S]*background:\s*#fff/)
})

test('生成/保存按钮不灰置 + 卡片响应式', async () => {
  const tv = await read('./views/TextView.vue')
  const iv = await read('./views/ImageView.vue')
  const tw = await read('./components/TweakDrawer.vue')
  assert.doesNotMatch(tv, /:disabled/)
  assert.doesNotMatch(iv, /:disabled/)
  assert.doesNotMatch(tw, /:disabled/)
  // A.14 响应式仅作用于上传卡片（ImageView；TextView 为文本页无 upload-card）
  assert.match(iv, /width:\s*min\(875px,\s*calc\(100vw\s*-\s*64px\)\)/)
  assert.match(tv, /:focus/)   // 输入框 focus 主色边框+外发光
})

test('路由懒加载 + 页脚链接', async () => {
  const router = await read('./router.js')
  const footer = await read('./components/AppFooter.vue')
  assert.match(router, /\(\)\s*=>\s*import\(/)
  assert.match(footer, /href="https:\/\/lazycat\.cloud\/"/)
})

test('model-select focus 有可见 outline', async () => {
  const tv = await read('./views/TextView.vue')
  assert.match(tv, /\.model-select:focus\s*\{[\s\S]*outline:\s*2px\s+solid\s+var\(--red\)/)
})
