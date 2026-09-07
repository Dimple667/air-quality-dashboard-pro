<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAirStore } from '../stores/air'
import StatCard from '../components/StatCard.vue'
import Panel from '../components/Panel.vue'
import SkeletonPanel from '../components/SkeletonPanel.vue'
import TrendChart from '../components/TrendChart.vue'
import RegionBarChart from '../components/RegionBarChart.vue'
import LevelPieChart from '../components/LevelPieChart.vue'
import ChinaMap from '../components/ChinaMap.vue'
import AlertList from '../components/AlertList.vue'
import RankingTable from '../components/RankingTable.vue'

const store = useAirStore()
const { data, cities, selectedCity, loading, error, alerts, selectedCityInfo, refreshSeconds } = storeToRefs(store)
let countdownTimer = 0

const refreshText = computed(() => {
  const m = Math.floor(refreshSeconds.value / 60)
  const s = String(refreshSeconds.value % 60).padStart(2, '0')
  return `${m}:${s}`
})

async function handleSelect(city: string) {
  if (city === selectedCity.value) return
  await store.selectCity(city)
}

onMounted(async () => {
  await store.init()
  countdownTimer = window.setInterval(async () => {
    store.tickCountdown()
    if (refreshSeconds.value <= 0) await store.refresh()
  }, 1000)
})
onBeforeUnmount(() => window.clearInterval(countdownTimer))
</script>

<template>
  <main class="dashboard-shell">
    <div class="bg-grid"></div>
    <div class="bg-glow glow-a"></div>
    <div class="bg-glow glow-b"></div>

    <header class="hero">
      <div>
        <div class="eyebrow">AIR QUALITY INTELLIGENCE</div>
        <h1>中国空气质量监测可视化平台</h1>
        <p>Vue3 · TypeScript · ECharts · Flask · SQLite</p>
      </div>

      <div class="hero-actions">
        <label class="city-select" for="city-filter">
          <span>城市</span>
          <select id="city-filter" name="city" :value="selectedCity" @change="handleSelect(($event.target as HTMLSelectElement).value)">
            <option value="">全国概览</option>
            <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
          </select>
        </label>
        <button class="refresh-btn" :disabled="loading" @click="store.refresh()">
          {{ loading ? '刷新中…' : `刷新 ${refreshText}` }}
        </button>
      </div>
    </header>

    <div v-if="error" class="error-banner">
      <span>{{ error }}</span>
      <button @click="store.refresh()">重新加载</button>
    </div>

    <template v-if="loading && !data">
      <section class="stats-grid">
        <div v-for="i in 4" :key="i" class="stat-card skeleton-card">
          <div class="skeleton skeleton-big"></div>
          <div class="skeleton skeleton-small"></div>
        </div>
      </section>
      <section class="dashboard-grid"><SkeletonPanel v-for="i in 4" :key="i" /></section>
    </template>

    <template v-else-if="data">
      <section class="stats-grid">
        <StatCard label="监测城市" :value="data.total_cities" hint="城市覆盖" />
        <StatCard label="平均 AQI" :value="data.avg_aqi" hint="实时均值" />
        <StatCard label="优良城市" :value="data.good_cities" hint="AQI ≤ 100" />
        <StatCard label="污染城市" :value="data.polluted_cities" hint="AQI > 100" />
      </section>

      <section v-if="selectedCityInfo" class="city-highlight">
        <div>
          <span class="highlight-label">当前关注城市</span>
          <strong>{{ selectedCityInfo.city }}</strong>
          <small>{{ selectedCityInfo.province }}</small>
        </div>
        <div class="highlight-metrics">
          <span><b>{{ selectedCityInfo.aqi }}</b>AQI</span>
          <span><b>{{ selectedCityInfo.pm25 }}</b>PM2.5</span>
          <span><b>{{ selectedCityInfo.pm10 }}</b>PM10</span>
          <span><b>{{ selectedCityInfo.quality_level }}</b>等级</span>
        </div>
      </section>

      <section class="dashboard-grid">
        <Panel class="map-panel" title="中国空气质量分布" subtitle="点击城市散点可联动筛选">
          <ChinaMap :cities="data.city_ranking" :selected-city="selectedCity" @select-city="handleSelect" />
        </Panel>

        <Panel title="空气质量趋势" :subtitle="`${data.selected_city} 近 7 日`">
          <TrendChart :city="data.selected_city" :trend="data.trend" />
        </Panel>

        <Panel title="区域 AQI 分析" subtitle="各区域平均 AQI">
          <RegionBarChart :regions="data.region_stats" />
        </Panel>

        <Panel title="污染等级分布" subtitle="城市空气质量等级占比">
          <LevelPieChart :distribution="data.level_distribution" />
        </Panel>

        <Panel title="实时预警" subtitle="AQI > 100">
          <AlertList :alerts="alerts" />
        </Panel>

        <Panel title="城市空气质量排名" subtitle="点击城市查看详情">
          <RankingTable :rows="data.city_ranking" :selected-city="selectedCity" @select-city="handleSelect" />
        </Panel>
      </section>

      <footer class="footer">
        <span>数据更新时间：{{ data.update_time }}</span>
        <span>演示数据 · 可替换为你的爬虫 + SQLite 数据源</span>
      </footer>
    </template>

    <div v-else class="empty-dashboard">
      <p>暂无可展示的空气质量数据，请确认后端服务已启动。</p>
      <button class="refresh-btn" @click="store.refresh()">重新加载</button>
    </div>
  </main>
</template>
