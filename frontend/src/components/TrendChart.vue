<script setup lang="ts">
import * as echarts from 'echarts'
import { computed, ref, watch } from 'vue'
import { useECharts } from '../composables/useECharts'
import type { TrendPoint } from '../types/air'

const props = defineProps<{ city: string; trend: TrendPoint[] }>()
const el = ref<HTMLDivElement | null>(null)
const isEmpty = computed(() => props.trend.length === 0)
const { setOption, clear } = useECharts(el, render)

function render() {
  if (isEmpty.value) {
    clear()
    return
  }
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(5,18,33,.96)', borderColor: 'rgba(83,191,255,.5)', textStyle: { color: '#eaf6ff' } },
    legend: { data: ['AQI', 'PM2.5'], right: 8, textStyle: { color: '#9fb8d0' } },
    grid: { left: 44, right: 22, top: 44, bottom: 28 },
    xAxis: { type: 'category', data: props.trend.map(i => i.date.slice(5)), boundaryGap: false, axisLine: { lineStyle: { color: '#31516d' } }, axisLabel: { color: '#8da7bf' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(120,160,190,.12)' } }, axisLabel: { color: '#8da7bf' } },
    series: [
      { name: 'AQI', type: 'line', smooth: true, data: props.trend.map(i => i.aqi), symbolSize: 7, lineStyle: { width: 3 }, areaStyle: { opacity: .12 } },
      { name: 'PM2.5', type: 'line', smooth: true, data: props.trend.map(i => i.pm25), symbolSize: 6, lineStyle: { width: 2 } }
    ]
  }
  setOption(option)
}
watch(() => props.trend, render, { deep: true })
</script>

<template>
  <div class="chart-wrap">
    <div v-if="isEmpty" class="chart-empty">暂无趋势数据</div>
    <div ref="el" class="chart"></div>
  </div>
</template>
