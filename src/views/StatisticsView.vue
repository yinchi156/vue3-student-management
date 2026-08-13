<template>
    <div class="statistics-container">
        <h2>📊 各科平均分统计</h2>
        <div class="chart-wrapper">
            <div ref="chartRef" style="width: 30%; height: 300px;"></div>
            <div ref="pieChartRef" style="width: 30%; height: 300px;"></div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import * as echarts from 'echarts'

const chartRef = ref(null)
const pieChartRef = ref(null)
let chartInstance = null
let pieChartInstance = null

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

const loadGradeDistribution = async () => {
    try {
        const res = await request.get('/statistics/grade-level-distribution')
        if (res.data.code === 200) {
            const data = res.data.data
            renderPieChart(data)
        } else {
            ElMessage.error(res.data.message || '加载失败')
        }
    } catch {
        ElMessage.error('获取成绩等级分布失败')
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

        }))
    }

    chartInstance.setOption(option)

    // 窗口大小变化时自适应
    window.addEventListener('resize', handleResize)
}

const renderPieChart = (data) => {
    if (!pieChartRef.value) return
    if (pieChartInstance) pieChartInstance.dispose()

    pieChartInstance = echarts.init(pieChartRef.value)

    const option = {
        title: {
            text: '成绩等级分布',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c}人 ({d}%)'
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            top: 'center',
            itemGap: 40
        },
        series: [
            {
                name: '等级分布',   // 系列名称（在 tooltip 中显示）
                type: 'pie',        // 图表类型：饼图
                radius: ['40%', '70%'],  // 内径 40%，外径 70%（形成环形图）
                avoidLabelOverlap: false, // 标签不自动避让重叠
                itemStyle: {
                    borderRadius: 10,     // 扇形块圆角
                    borderColor: '#fff',  // 边框颜色（白色）
                    borderWidth: 2        // 边框宽度
                },
                label: {
                    show: true,           // 显示标签
                    formatter: '{b}\n{d}%',// 显示：等级名称 + 百分比（换行）

                },
                emphasis: {
                    label: {
                        show: true,       // 悬停时显示标签
                        fontSize: 16,     // 悬停时放大字号
                        fontWeight: 'bold' // 悬停时加粗
                    }
                },
                data: data
            }
        ]
    }

    pieChartInstance.setOption(option)
}

const handleResize = () => {
    if (chartInstance) {
        chartInstance.resize()
    }
}

onMounted(() => {
    loadStatistics()
    loadGradeDistribution()
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
    padding: 8px;
    border-radius: 12px;
}
</style>