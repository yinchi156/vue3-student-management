<template>
    <div>
        <div class="page-title">📊 成绩管理</div>
        <div class="content-card">
            <!-- 筛选条件 -->
            <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px;">
                <el-select v-model="selectedClass" placeholder="选择班级" style="width: 150px;" @change="onClassChange">
                    <el-option v-for="cls in classList" :key="cls.id" :label="cls.grade + cls.class + '班'"
                        :value="cls.id" />
                </el-select>
                <el-select v-model="selectedExam" placeholder="选择考试" style="width: 150px;">
                    <el-option v-for="exam in examList" :key="exam.id" :label="exam.name" :value="exam.id" />
                </el-select>
                <el-button type="primary" @click="loadStudents">加载学生</el-button>
                <el-button type="success" @click="saveAllScores">💾 保存全部</el-button>
            </div>

            <!-- 成绩表格 -->
            <div v-if="students.length === 0" class="empty-tip">
                请选择班级和考试，点击「加载学生」
            </div>
            <el-table v-else :data="students" max-height="500" stripe v-loading="loading" style="width: 100%;">
                <!-- 姓名 -->
                <el-table-column prop="name" label="姓名" width="100" fixed />
                <!-- 总分 -->
                <el-table-column label="总分" width="100" fixed>
                    <template #default="{ row }">
                        {{ row.total_score !== undefined ? row.total_score : '-' }}
                    </template>
                </el-table-column>
                <!-- 各科分数 -->
                <el-table-column v-for="subject in subjectList" :key="subject.id" :label="subject.subject" width="120">
                    <template #default="{ row }">
                        <el-input-number v-model="row.scores[subject.id]" :min="0" :max="subject.full_score" :step="0.5"
                            :precision="1" size="small" controls-position="right" style="width: 100px;"
                            @change="onScoreChange(row)" />
                        <span style="font-size: 11px; color: #999; margin-left: 2px;">/{{ subject.full_score }}</span>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 统计信息 -->
            <div v-if="students.length > 0"
                style="margin-top: 20px; background: #f8fafc; padding: 16px; border-radius: 8px; display: flex; flex-wrap: wrap; gap: 20px;">
                <div><strong>学生人数：</strong>{{ students.length }}</div>
                <div><strong>平均总分：</strong>{{ stats.avg_total || '-' }}</div>
                <div><strong>最高总分：</strong>{{ stats.max_total || '-' }}</div>
                <div><strong>最低总分：</strong>{{ stats.min_total || '-' }}</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { useRoute } from 'vue-router'

const route = useRoute()
// 筛选条件
const classList = ref([])
const examList = ref([])
const subjectList = ref([])
const selectedClass = ref('')
const selectedExam = ref('')
const students = ref([])
const loading = ref(false)

// 统计
const stats = computed(() => {
    if (students.value.length === 0) {
        return { avg_total: '-', max_total: '-', min_total: '-' }
    }
    const totals = students.value.map(s => s.total_score || 0)
    const sum = totals.reduce((a, b) => a + b, 0)
    return {
        avg_total: (sum / totals.length).toFixed(1),
        max_total: Math.max(...totals),
        min_total: Math.min(...totals)
    }
})

// 加载班级列表
const loadClassList = async () => {
    try {
        const res = await request.get('/teacher/classes')
        if (res.data.code === 200) {
            classList.value = res.data.data || []
            // 如果有 URL 参数，自动选中对应的班级
            const classIdFromUrl = route.query.classId
            if (classIdFromUrl) {
                selectedClass.value = Number(classIdFromUrl)
                // 触发班级变更，加载科目
                await onClassChange(selectedClass.value)
                // 加载考试列表
                await loadExamList()
                // 加载学生数据
                await loadStudents()
            }
        }
    } catch {
        ElMessage.error('加载班级列表失败')
    }
}

// 加载考试列表
const loadExamList = async () => {
    try {
        const res = await request.get('/exams')
        if (res.data.code === 200) {
            examList.value = res.data.data || []
            if (examList.value.length > 0) {
                selectedExam.value = examList.value[0].id
            }
        }
    } catch {
        ElMessage.error('加载考试列表失败')
    }
}

// 选择班级时加载科目
const onClassChange = async (classId) => {
    if (!classId) {
        subjectList.value = []
        return
    }
    try {
        const res = await request.get(`/subjects/by-class/${classId}`)
        if (res.data.code === 200) {
            subjectList.value = res.data.data || []
        }
    } catch {
        ElMessage.error('加载科目列表失败')
    }
}

// 加载学生数据
const loadStudents = async () => {
    if (!selectedClass.value) {
        ElMessage.warning('请先选择班级')
        return
    }
    if (!selectedExam.value) {
        ElMessage.warning('请先选择考试')
        return
    }

    loading.value = true
    try {
        const res = await request.get(`/students/by-class/${selectedClass.value}`, {
            params: { exam_id: selectedExam.value }
        })
        if (res.data.code === 200) {
            const data = res.data.data || []
            // 初始化每个学生的分数对象
            students.value = data.map(student => {
                const scores = {}
                let total = 0
                subjectList.value.forEach(sub => {
                    const existing = student.scores?.find(s => s.subject_id === sub.id)
                    const score = existing ? existing.score : null
                    scores[sub.id] = score//存储为数组
                    //判断分数累加，有就加，没有则不加
                    if (score !== null && score !== undefined && score !== '') {
                        total += Number(score)
                    }
                })

                return {
                    ...student,
                    scores: scores,
                    total_score: total
                }
            })
        } else {
            ElMessage.error(res.data.message || '加载失败')
        }
    } catch {
        ElMessage.error('加载学生数据失败')
    } finally {
        loading.value = false
    }
}

// 分数变化时更新总分
const onScoreChange = (row) => {
    let total = 0
    let hasScore = false
    subjectList.value.forEach(sub => {
        const score = row.scores[sub.id]
        if (score !== null && score !== undefined && score !== '') {
            total += Number(score)
            hasScore = true
        }
    })
    row.total_score = hasScore ? total : 0
}

// 保存全部成绩
const saveAllScores = async () => {
    if (students.value.length === 0) {
        ElMessage.warning('没有可保存的数据')
        return
    }

    // 收集所有有分数的记录
    const allScores = []
    students.value.forEach(student => {
        subjectList.value.forEach(sub => {
            const score = student.scores[sub.id]
            if (score !== null && score !== undefined && score !== '') {
                allScores.push({
                    student_id: student.id,
                    subject_id: sub.id,
                    score: Number(score)
                })
            }
        })
    })

    if (allScores.length === 0) {
        ElMessage.warning('没有可保存的分数')
        return
    }

    try {
        const res = await request.post('/scores/batch', {
            class_id: selectedClass.value,
            exam_id: selectedExam.value,
            scores: allScores
        })
        if (res.data.code === 200) {
            ElMessage.success(res.data.message || '保存成功')
        } else {
            ElMessage.error(res.data.message || '保存失败')
        }
    } catch (error) {
        const msg = error.response?.data?.message || '保存失败'
        ElMessage.error(msg)
    }
}

onMounted(() => {
    loadClassList()
    loadExamList()
})
</script>

<style scoped>
.page-title {
    font-size: 20px;
    font-weight: 600;
    color: #1e2a3a;
    margin-bottom: 20px;
}

.content-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.empty-tip {
    text-align: center;
    color: #8896a8;
    padding: 40px 0;
}
</style>