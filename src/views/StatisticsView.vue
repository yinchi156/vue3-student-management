<template>
    <div class="statistics-container">
        <h2>📊 各科平均分统计</h2>
        <div class="chart-wrapper">
            <div ref="chartRef" style="width: 100%; height: 400px;"></div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chartInstance = null

// 加载数据并渲染图表
const loadStatistics = async () => {
    try {
        const res = await request.get('/statistics/subject-averages')
        if (res.data.code === 200) {
            const data = res.data.data
            renderChart(data)
        } else {
            ElMessage.error(res.data.message || '加载失败')
        }
    } catch {
        ElMessage.error('获取统计数据失败')
    }
}

// 渲染柱状图
const renderChart = (data) => {
    if (!chartRef.value) return
    if (chartInstance) chartInstance.dispose()

    chartInstance = echarts.init(chartRef.value)

    const option = {
        title: {
            text: '各年级各科平均分对比',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: {
            data: data.grades,
            top: 50
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '1%',
            top: '30%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: data.subjects,
            axisLabel: { fontSize: 14 }
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 100,
            axisLabel: { fontSize: 14 },
            splitLine: { lineStyle: { type: 'dashed' } }
        },
        series: data.series.map((item, index) => ({
            name: item.name,
            type: 'bar',
            data: item.data,
            barWidth: '20%',
            label: {
                show: true,
                position: 'top',
                formatter: (params) => params.value + '分'
            }
        }))
    }

    chartInstance.setOption(option)

    // 窗口大小变化时自适应
    window.addEventListener('resize', handleResize)
}

const handleResize = () => {
    if (chartInstance) {
        chartInstance.resize()
    }
}

onMounted(() => {
    loadStatistics()
})

onUnmounted(() => {
    if (chartInstance) {
        chartInstance.dispose()
    }
    window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.statistics-container {
    padding: 24px;
}

.statistics-container h2 {
    font-size: 20px;
    color: #1e2a3a;
    margin-bottom: 20px;
}

.chart-wrapper {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
</style>