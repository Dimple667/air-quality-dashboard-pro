import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, type Ref } from 'vue'

/**
 * ECharts 生命周期封装，所有图表组件共用：
 * - mounted 后再 init，同一 DOM 只初始化一次
 * - 卸载时 dispose，避免内存泄漏
 * - 窗口 resize 自动调用 chart.resize()
 * - onReady 在图表初始化完成后触发，用于首帧渲染
 */
export function useECharts(el: Ref<HTMLDivElement | null>, onReady?: () => void) {
  let chart: echarts.ECharts | null = null

  function resize() {
    chart?.resize()
  }

  function ensureInit() {
    if (chart || !el.value) return
    chart = echarts.init(el.value)
    window.addEventListener('resize', resize)
    onReady?.()
  }

  function setOption(option: echarts.EChartsOption, notMerge = true) {
    ensureInit()
    chart?.setOption(option, notMerge)
  }

  function clear() {
    chart?.clear()
  }

  function getChart() {
    return chart
  }

  function dispose() {
    window.removeEventListener('resize', resize)
    chart?.dispose()
    chart = null
  }

  onMounted(ensureInit)
  onBeforeUnmount(dispose)

  return { getChart, setOption, clear, resize, dispose }
}
