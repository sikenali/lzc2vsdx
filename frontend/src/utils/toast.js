/**
 * 统一 Toast 助手（DESIGN §9）。
 * type ∈ { success, error, warning, info }；App.vue 监听 c2vsdx-toast 的 {type,message}。
 */
export function toast(type = 'info', message = '') {
  window.dispatchEvent(new CustomEvent('c2vsdx-toast', { detail: { type, message } }))
}
