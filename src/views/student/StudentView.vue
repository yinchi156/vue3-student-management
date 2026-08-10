<template>
    <div class="student-container">
        <!-- 学生信息 -->
        <div class="student-info">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2>{{ studentName }}</h2>
                    <div class="sub">班级：{{ studentClass }}</div>
                </div>
                <el-button size="small" @click="handleLogout">退出登录</el-button>
            </div>
        </div>

        <!-- 成绩概览 -->
        <div class="summary">
            <div class="summary-item">
                <div class="value">{{ totalScore }}</div>
                <div class="label">总分</div>
            </div>
            <div class="summary-item">
                <div class="value">{{ avgScore }}</div>
                <div class="label">平均分</div>
            </div>
            <div class="summary-item">
                <div class="value">{{ subjectCount }}</div>
                <div class="label">科目数</div>
            </div>
        </div>

        <!-- 成绩列表 -->
        <el-table :data="scoreList" border stripe v-loading="loading" style="width: 100%;">
            <el-table-column prop="subject" label="科目" />
            <el-table-column label="分数" width="120">
                <template #default="{ row }">
                    <span :class="row.score >= row.full_score * 0.6 ? 'score-pass' : 'score-fail'">
                        {{ row.score }}
                    </span>
                </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
                <template #default="{ row }">
                    <el-tag :type="row.score >= row.full_score * 0.6 ? 'success' : 'danger'">
                        {{ row.score >= row.full_score * 0.6 ? '及格' : '不及格' }}
                    </el-tag>
                </template>
            </el-table-column>
        </el-table>

        <div v-if="!loading && scoreList.length === 0" class="empty-tip">
            📭 暂无成绩数据
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

// 学生信息
const studentName = ref('加载中...')
const studentClass = ref('-')
const scoreList = ref([])
const loading = ref(false)


const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('studentId')
    window.location.href = '/login'
}

// 从 localStorage 获取当前学生 ID（假设登录时存了 studentId）
// 如果没有，可以从后端 /api/me 获取
const studentId = ref(Number(localStorage.getItem('studentId')) || 72)

// 计算属性：总分
const totalScore = computed(() => {
    return scoreList.value.reduce((sum, item) => sum + item.score, 0)
})

// 计算属性：平均分
const avgScore = computed(() => {
    if (scoreList.value.length === 0) return 0
    return (totalScore.value / scoreList.value.length).toFixed(1)
})

// 计算属性：科目数
const subjectCount = computed(() => {
    return scoreList.value.length
})

// 加载学生成绩
const loadStudentData = async () => {
    loading.value = true
    try {
        const res = await request.get(`/student/${studentId.value}/scores`)
        if (res.data.code === 200) {
            const data = res.data.data
            studentName.value = data.name || '未命名'
            studentClass.value = data.class_name || '-'
            scoreList.value = data.scores || []
        } else {
            ElMessage.error(res.data.message || '加载失败')
        }
    } catch {
        ElMessage.error('加载数据失败')
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    loadStudentData()
})
</script>

<style scoped>
.student-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.student-info {
    background: white;
    padding: 20px 24px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    margin-bottom: 24px;
}

.student-info h2 {
    font-size: 20px;
    color: #1e2a3a;
    margin-bottom: 4px;
}

.student-info .sub {
    color: #8896a8;
    font-size: 14px;
}

.summary {
    display: flex;
    gap: 24px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}

.summary-item {
    background: white;
    padding: 16px 24px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    flex: 1;
    min-width: 120px;
    text-align: center;
}

.summary-item .value {
    font-size: 24px;
    font-weight: 600;
    color: #1e2a3a;
}

.summary-item .label {
    font-size: 13px;
    color: #8896a8;
    margin-top: 4px;
}

.score-pass {
    color: #27ae60;
    font-weight: 600;
}

.score-fail {
    color: #e74c3c;
    font-weight: 600;
}

.empty-tip {
    text-align: center;
    padding: 40px;
    color: #8896a8;
}
</style>