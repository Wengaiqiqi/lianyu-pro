<template>
  <div ref="chartEl" :style="{ width: '100%', height: height + 'px' }"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: Number, default: 300 },
})

const chartEl = ref()
let chart = null

onMounted(() => {
  chart = echarts.init(chartEl.value)
  chart.setOption(props.option)
  window.addEventListener('resize', () => chart?.resize())
})

watch(() => props.option, (val) => {
  chart?.setOption(val, true)
}, { deep: true })
</script>
