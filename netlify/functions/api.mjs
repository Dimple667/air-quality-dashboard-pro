// Netlify Function：线上版的 /api/* 接口。
//
// Netlify Functions 不支持 Python 运行时，所以聚合计算提前到构建阶段完成
// （scripts/export_snapshot.py），这里只负责把快照按接口契约返回。
//
// 网络请求由 netlify.toml 的 redirect 从 /api/* 重写到这里。

import snapshot from '../data/snapshot.mjs'

const JSON_HEADERS = {
  'content-type': 'application/json; charset=utf-8',
  // update_time 每次请求都要是新的，不能被 CDN 缓存
  'cache-control': 'no-store'
}

const respond = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: JSON_HEADERS })

/** 统一成功响应结构，与 backend/app.py 的 ok() 一致 */
const ok = (data) => respond({ code: 0, message: 'success', data })

/** 统一失败响应结构，与 backend/app.py 的 fail() 一致 */
const fail = (message, code = 500) => respond({ code, message, data: null }, code)

const ROUTES = ['/health', '/cities', '/dashboard_data']

/**
 * /api/* 经 redirect 重写后，pathname 可能是：
 *   /api/dashboard_data
 *   /.netlify/functions/api/dashboard_data
 * 这里统一归一化成 /dashboard_data。
 */
function routePath(pathname) {
  const path = pathname.replace(/\/+$/, '') || '/'
  for (const prefix of ['/.netlify/functions/api', '/api']) {
    if (path === prefix) return '/'
    if (path.startsWith(prefix + '/')) return path.slice(prefix.length)
  }
  return path
}

/**
 * 'sv-SE' 的日期格式恰好是 YYYY-MM-DD HH:mm:ss，
 * 固定用东八区，避免函数跑在 UTC 上导致时间显示差 8 小时。
 */
const nowText = () =>
  new Date().toLocaleString('sv-SE', { timeZone: 'Asia/Shanghai' })

export default async (req) => {
  const url = new URL(req.url)
  const route = routePath(url.pathname)

  if (!ROUTES.includes(route)) return fail('接口不存在', 404)
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return fail('请求方法不允许', 405)
  }

  if (route === '/health') return ok({ status: 'ok' })
  if (route === '/cities') return ok(snapshot.cities)

  const requested = (url.searchParams.get('city') || '').trim()
  const city = snapshot.cities.includes(requested)
    ? requested
    : snapshot.default_city

  return ok({
    ...snapshot.shared,
    selected_city: city,
    trend: snapshot.trends[city] ?? [],
    update_time: nowText()
  })
}
