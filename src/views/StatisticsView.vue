<template>
    <div class="statistics-container">
        <h2>📊 数据统计</h2>
        <div class="chart-wrapper">
            <!-- 第一行：柱状图 + 饼图 -->
            <div class="chart-row">
                <div ref="chartRef" class="chart-box"></div>
                <div ref="pieChartRef" class="chart-box"></div>
            </div>
            <!-- 第二行：折线图（全宽） -->
            <div ref="trendChartRef" class="chart-box full-width"></div>
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
const trendChartRef = ref(null)

let chartInstance = null
let pieChartInstance = null
let trendChartInstance = null

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

const loadTrendData = async () => {
    try {
        const res = await request.get('/statistics/avg-trend')
        if (res.data.code === 200) {
            const data = res.data.data
            renderTrendChart(data)
        } else {
            ElMessage.error(res.data.message || '加载失败')
        }
    } catch (error) {
        console.error('获取趋势数据失败:', error)
        ElMessage.error('获取趋势数据失败')
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
            bottom: '10%',
            top: '30%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: data.subjects,
            axisLabel: { fontSize: 13 }
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 100,
            axisLabel: { fontSize: 13 },
            splitLine: { lineStyle: { type: 'dashed' } }
        },
        series: data.series.map((item) => ({
            name: item.name,
            type: 'bar',
            data: item.data,
            barWidth: '25%',

        }))
    }

    chartInstance.setOption(option)
}

// 渲染饼图
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
            top: 'center'
        },
        series: [
            {
                name: '等级分布',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: true,
                    formatter: '{b}\n{d}%'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 16,
                        fontWeight: 'bold'
                    }
                },
                data: data
            }
        ]
    }

    pieChartInstance.setOption(option)
}

// 渲染折线图
const renderTrendChart = (data) => {
    if (!trendChartRef.value) return
    if (trendChartInstance) trendChartInstance.dispose()

    trendChartInstance = echarts.init(trendChartRef.value)

    const option = {
        title: {
            text: '班级平均分趋势',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            formatter: (params) => {
                const p = params[0]
                return `${p.name}<br/>平均分：${p.value} 分`
            }
        },
        grid: {
            left: '8%',
            right: '8%',
            bottom: '15%',
            top: '20%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: data.exams,
            axisLabel: { fontSize: 13 }
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: data.max_score || 100,
            axisLabel: {
                fontSize: 13,
                formatter: '{value} 分'
            },
            splitLine: { lineStyle: { type: 'dashed' } }
        },
        series: [
            {
                name: '平均分',
                type: 'line',
                data: data.avg_scores,
                smooth: true,
                symbol: 'circle',
                symbolSize: 8,
                lineStyle: {
                    width: 3,
                    color: '#409eff'
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
                            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
                        ]
                    }
                },

            }
        ]
    }

    trendChartInstance.setOption(option)
}

// 窗口大小变化自适应
const handleResize = () => {
    if (chartInstance) chartInstance.resize()
    if (pieChartInstance) pieChartInstance.resize()
    if (trendChartInstance) trendChartInstance.resize()
}

onMounted(() => {
    loadStatistics()
    loadGradeDistribution()
    loadTrendData()
    window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
    if (chartInstance) chartInstance.dispose()
    if (pieChartInstance) pieChartInstance.dispose()
    if (trendChartInstance) trendChartInstance.dispose()
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
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.chart-row {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
}

.chart-box {
    flex: 1;
    height: 300px;
    min-width: 0;
}

.full-width {
    width: 100%;
    height: 350px;
}
</style>