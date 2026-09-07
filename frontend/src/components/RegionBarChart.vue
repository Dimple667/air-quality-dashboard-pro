<script setup lang="ts">
import * as echarts from 'echarts'
import { computed, ref, watch } from 'vue'
import { useECharts } from '../composables/useECharts'

const props = defineProps<{ regions: Record<string, number> }>()
const el = ref<HTMLDivElement | null>(null)
const isEmpty = computed(() => Object.keys(props.regions).length === 0)
const { setOption, clear } = useECharts(el, render)

function render() {
  if (isEmpty.value) {
    clear()
    return
  }
  const entries = Object.entries(props.regions)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: 42, right: 16, top: 24, bottom: 28 },
    xAxis: { type: 'category', data: entries.map(([k]) => k), axisLine: { lineStyle: { color: '#31516d' } }, axisLabel: { color: '#8da7bf' } },
    yAxis: { type: 'value', axisLabel: { color: '#8da7bf' }, splitLine: { lineStyle: { color: 'rgba(120,160,190,.12)' } } },
    series: [{
      type: 'bar',
      data: entries.map(([, v]) => v),
      barMaxWidth: 34,
      itemStyle: {
        borderRadius: [7, 7, 0, 0],
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#5bd4ff' }, { offset: 1, color: '#3654d8' }] }
      }
    }]
  }
  setOption(option)
}
watch(() => props.regions, render, { deep: true })
</script>

<template>
  <div class="chart-wrap">
    <div v-if="isEmpty" class="chart-empty">暂无区域数据</div>
    <div ref="el" class="chart"></div>
  </div>
</template>
