<script setup lang="ts">
import type { CityAir } from '../types/air'
defineProps<{ rows: CityAir[]; selectedCity: string }>()
const emit = defineEmits<{ (e: 'select-city', city: string): void }>()
</script>

<template>
  <div class="ranking-table">
    <div v-if="rows.length === 0" class="empty-state">暂无排名数据</div>
    <button v-for="(item, index) in rows" :key="item.city" :class="['ranking-row', { active: item.city === selectedCity }]" @click="emit('select-city', item.city)">
      <span class="rank">#{{ index + 1 }}</span>
      <span class="city">{{ item.city }}</span>
      <span class="aqi">AQI {{ item.aqi }}</span>
      <span class="level">{{ item.quality_level }}</span>
    </button>
  </div>
</template>
