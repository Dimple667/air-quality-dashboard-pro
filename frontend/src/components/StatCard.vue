<script setup lang="ts">
defineProps<{ label: string; value: string | number; hint?: string }>()
</script>

<template>
  <article class="stat-card">
    <div class="stat-glow"></div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
    <div v-if="hint" class="stat-hint">{{ hint }}</div>
  </article>
</template>
