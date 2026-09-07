<script setup lang="ts">
import * as echarts from 'echarts'
import { computed, onMounted, ref, watch } from 'vue'
import { useECharts } from '../composables/useECharts'
import type { CityAir } from '../types/air'

const props = defineProps<{ cities: CityAir[]; selectedCity: string }>()
const emit = defineEmits<{ (e: 'select-city', city: string): void }>()

const el = ref<HTMLDivElement | null>(null)
const mapMessage = ref('地图加载中…')
const isEmpty = computed(() => props.cities.length === 0)
const { getChart, setOption, clear } = useECharts(el)
let mapReady = false

function aqiColor(aqi: number) {
  if (aqi <= 50) return '#46e6a5'
  if (aqi <= 100) return '#9fe870'
  if (aqi <= 150) return '#ffd35a'
  if (aqi <= 200) return '#ff8b63'
  return '#d977ff'
}

function getSeriesData() {
  return props.cities.map(city => ({
    name: city.city,
    value: [city.lng, city.lat, city.aqi],
    itemStyle: { color: aqiColor(city.aqi) }
  }))
}

function renderMap() {
  if (isEmpty.value) {
    clear()
    return
  }
  if (!mapReady) return
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const city = props.cities.find(c => c.city === params.name)
        return city ? `${city.city}<br/>AQI：${city.aqi}<br/>PM2.5：${city.pm25}<br/>${city.quality_level}` : params.name
      }
    },
    geo: {
      map: 'china',
      roam: true,
      zoom: 1.1,
      layoutCenter: ['50%', '51%'],
      layoutSize: '94%',
      itemStyle: { areaColor: '#0d2740', borderColor: '#3f9fd4', borderWidth: 1, shadowBlur: 14, shadowColor: 'rgba(44,155,255,.22)' },
      emphasis: { itemStyle: { areaColor: '#16466d' } }
    },
    series: [{
      type: 'effectScatter',
      coordinateSystem: 'geo',
      data: getSeriesData(),
      rippleEffect: { brushType: 'stroke', scale: 3.2 },
      symbolSize: (val: number[]) => Math.max(8, Math.min(24, val[2] / 7)),
      emphasis: { scale: 1.45 },
      zlevel: 3
    }]
  }
  setOption(option, true)
}

function renderFallback() {
  mapMessage.value = 'GeoJSON 加载失败，已使用降级视图'
  const option: echarts.EChartsOption = {
    xAxis: { type: 'category', data: props.cities.map(c => c.city), axisLabel: { color: '#8da7bf', rotate: 30 } },
    yAxis: { type: 'value', axisLabel: { color: '#8da7bf' } },
    series: [{ type: 'scatter', data: props.cities.map(c => c.aqi), symbolSize: 18 }]
  }
  setOption(option, true)
}

async function loadMap() {
  try {
    const response = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    if (!response.ok) throw new Error()
    echarts.registerMap('china', await response.json())
    mapReady = true
    mapMessage.value = ''
    renderMap()
  } catch {
    renderFallback()
  }
}

function onClick(params: echarts.ECElementEvent) {
  if (params?.name && props.cities.some(c => c.city === params.name)) {
    emit('select-city', params.name)
  }
}

onMounted(() => {
  getChart()?.on('click', onClick)
  loadMap()
})
watch(() => props.cities, () => { if (mapReady) renderMap() }, { deep: true })
</script>

<template>
  <div class="map-wrap">
    <div v-if="mapMessage" class="map-message">{{ mapMessage }}</div>
    <div v-if="isEmpty" class="chart-empty">暂无城市数据</div>
    <div ref="el" class="chart"></div>
  </div>
</template>
