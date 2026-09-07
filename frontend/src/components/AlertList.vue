<script setup lang="ts">
import type { CityAir } from '../types/air'
defineProps<{ alerts: CityAir[] }>()
function severity(aqi: number) {
  if (aqi > 200) return 'danger'
  if (aqi > 150) return 'high'
  return 'warn'
}
</script>

<template>
  <div class="alert-list">
    <div v-if="alerts.length === 0" class="empty-state">当前暂无污染预警</div>
    <article v-for="city in alerts" :key="city.city" :class="['alert-row', severity(city.aqi)]">
      <div><strong>{{ city.city }}</strong><span>{{ city.province }}</span></div>
      <div class="alert-meta"><b>AQI {{ city.aqi }}</b><span>{{ city.quality_level }}</span></div>
    </article>
  </div>
</template>
