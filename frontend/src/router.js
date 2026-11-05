import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'text', component: () => import('./views/TextView.vue'), meta: { tab: 'text', subtitle: '文本生成 Visio 图' } },
  { path: '/image', name: 'image', component: () => import('./views/ImageView.vue'), meta: { tab: 'image', subtitle: '图片生成 Visio 图' } },
  {
    path: '/text/progress/:id',
    name: 'text-progress',
    component: () => import('./views/TextProgressView.vue'),
    meta: { tab: 'text', subtitle: '文本生成 Visio 图' },
  },
  {
    path: '/image/progress/:id',
    name: 'image-progress',
    component: () => import('./views/ImageProgressView.vue'),
    meta: { tab: 'image', subtitle: '图片生成 Visio 图' },
  },
  {
    path: '/result/:id',
    name: 'result',
    component: () => import('./views/ResultView.vue'),
    meta: { tab: 'image', subtitle: '生成结果' },
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
