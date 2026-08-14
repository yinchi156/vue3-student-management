<template>
    <div class="class-students">
        <div class="page-header">
            <h2>📋 班级学生列表</h2>
            <el-button type="default" @click="goBack">
                <el-icon>
                    <ArrowLeft />
                </el-icon> 返回
            </el-button>
        </div>

        <!-- 筛选条件 -->
        <div class="content-card">
            <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
                <el-select v-model="selectedClass" placeholder="选择班级" style="width: 180px;" @change="onClassChange">
                    <el-option v-for="cls in classList" :key="cls.id" :label="cls.grade + cls.class + '班'"
                        :value="cls.id" />
                </el-select>
                <el-select v-model="selectedExam" placeholder="选择考试" style="width: 180px;" @change="onExamChange">
                    <el-option v-for="exam in examList" :key="exam.id" :label="exam.name" :value="exam.id" />
                </el-select>
                <el-button type="primary" @click="loadStudents">查询</el-button>
            </div>
        </div>

        <!-- 学生列表 -->
        <div class="content-card" style="margin-top: 16px;">
            <div v-if="loading" class="empty-tip">⏳ 加载中...</div>
            <div v-else-if="students.length === 0" class="empty-tip">暂无学生数据</div>
            <el-table v-else :data="students" stripe style="width: 100%;">
                <el-table-column prop="id" label="序号" width="60" />
                <el-table-column prop="name" label="姓名" width="80" />
                <el-table-column prop="gender" label="性别" width="70">
                    <template #default="{ row }">
                        {{ row.gender === 1 ? '男' : '女' }}
                    </template>
                </el-table-column>
                <el-table-column prop="age" label="年龄" width="70" />
                <el-table-column v-for="subject in subjectList" :key="subject.id" :label="subject.subject" width="100">
                    <template #default="{ row }">
                        {{ row.scores?.[subject.id] ?? '-' }}
                    </template>
                </el-table-column>
                <el-table-column label="总分" width="100" fixed="right">
                    <template #default="{ row }">
                        {{ row.total_score ?? '-' }}
                    </template>
                </el-table-column>
            </el-table>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const classList = ref([])
const examList = ref([])
const subjectList = ref([])
const selectedClass = ref('')
const selectedExam = ref('')
const students = ref([])
const loading = ref(false)

// 返回
const goBack = () => {
    router.back()
}

// 加载教师的班级列表
const loadClassList = async () => {
    try {
        const res = await request.get('/teacher/classes')
        if (res.data.code === 200) {
            classList.value = res.data.data || []
            const classIdFromUrl = route.query.classId
            if (classIdFromUrl) {
                selectedClass.value = Number(classIdFromUrl)
                await onClassChange(selectedClass.value)
                await loadExamList()
                await loadStudents()
            }
        }
    } catch (error) {
        console.error('错误发生在哪里:', error)
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

// 切换考试
const onExamChange = () => {
    if (selectedClass.value && selectedExam.value) {
        loadStudents()
    }
}

// 加载学生数据
const loadStudents = async () => {
    if (!selectedClass.value) {
        ElMessage.warning('请选择班级')
        return
    }
    if (!selectedExam.value) {
        ElMessage.warning('请选择考试')
        return
    }

    loading.value = true
    try {
        const res = await request.get(`/students/by-class/${selectedClass.value}`, {
            params: { exam_id: selectedExam.value }
        })
        if (res.data.code === 200) {
            const data = res.data.data || []
            students.value = data.map(student => {
                const scores = {}
                let total = 0
                subjectList.value.forEach(sub => {
                    const existing = student.scores?.find(s => s.subject_id === sub.id)
                    const score = existing ? existing.score : null
                    scores[sub.id] = score
                    if (score !== null && score !== undefined && score !== '') {
                        total += Number(score)
                    }
                })
                return {
                    ...student,  // 保留 id, name, gender, age 等字段
                    scores: scores,
                    total_score: total
                }
            })
        } else {
            ElMessage.error(res.data.message || '加载失败')
            students.value = []
        }
    } catch {
        ElMessage.error('加载学生数据失败')
        students.value = []
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    loadClassList()
    loadExamList()
})
</script>

<style scoped>
.class-students {
    padding: 20px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.page-header h2 {
    font-size: 20px;
    color: #1e2a3a;
    margin: 0;
}

.content-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.empty-tip {
    text-align: center;
    color: #8896a8;
    padding: 40px 0;
}
</style>