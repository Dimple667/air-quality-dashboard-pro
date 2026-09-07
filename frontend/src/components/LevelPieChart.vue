<script setup lang="ts">
import * as echarts from 'echarts'
import { computed, ref, watch } from 'vue'
import { useECharts } from '../composables/useECharts'

const props = defineProps<{ distribution: Record<string, number> }>()
const el = ref<HTMLDivElement | null>(null)
const isEmpty = computed(() => Object.keys(props.distribution).length === 0)
const { setOption, clear } = useECharts(el, render)

function render() {
  if (isEmpty.value) {
    clear()
    return
  }
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: '#8da7bf' } },
    series: [{ type: 'pie', radius: ['48%', '72%'], center: ['50%', '44%'], label: { color: '#d9eaf7' }, data: Object.entries(props.distribution).map(([name, value]) => ({ name, value })) }]
  }
  setOption(option)
}
watch(() => props.distribution, render, { deep: true })
</script>

<template>
  <div class="chart-wrap">
    <div v-if="isEmpty" class="chart-empty">暂无分布数据</div>
    <div ref="el" class="chart"></div>
  </div>
</template>
