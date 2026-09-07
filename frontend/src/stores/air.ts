import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { getCities, getDashboardData } from '../api/dashboard'
import type { DashboardData } from '../types/air'

export const useAirStore = defineStore('air', () => {
  const data = ref<DashboardData | null>(null)
  const cities = ref<string[]>([])
  const selectedCity = ref('')
  const loading = ref(false)
  const error = ref('')
  const refreshSeconds = ref(300)

  const alerts = computed(() =>
    (data.value?.city_ranking || []).filter(item => item.aqi > 100)
  )

  const selectedCityInfo = computed(() => {
    if (!data.value) return null
    const name = selectedCity.value || data.value.selected_city
    return data.value.city_ranking.find(item => item.city === name) || null
  })

  async function init() {
    try {
      cities.value = await getCities()
    } catch (e) {
      error.value = e instanceof Error ? e.message : '城市列表获取失败'
      console.error('[store] 城市列表加载失败:', e)
    }
    await refresh()
  }

  async function refresh() {
    loading.value = true
    error.value = ''
    try {
      data.value = await getDashboardData(selectedCity.value)
      refreshSeconds.value = 300
    } catch (e) {
      error.value = e instanceof Error ? e.message : '数据请求失败'
      console.error('[store] 数据加载失败:', e)
    } finally {
      loading.value = false
    }
  }

  async function selectCity(city: string) {
    selectedCity.value = city
    await refresh()
  }

  function tickCountdown() {
    refreshSeconds.value = Math.max(0, refreshSeconds.value - 1)
  }

  return {
    data, cities, selectedCity, loading, error, alerts,
    selectedCityInfo, refreshSeconds, init, refresh, selectCity, tickCountdown
  }
})
