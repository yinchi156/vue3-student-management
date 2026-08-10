<template>
    <div>
        <div class="page-title">✏️ 成绩录入</div>
        <div class="content-card">
            <!-- 筛选条件 -->
            <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px;">
                <el-select v-model="selectedClass" placeholder="选择班级" style="width: 150px;">
                    <el-option v-for="cls in classList" :key="cls.id" :label="cls.grade + cls.class + '班'"
                        :value="cls.id" />
                </el-select>
                <el-select v-model="selectedSubject" placeholder="选择科目" style="width: 150px;">
                    <el-option v-for="sub in subjectList" :key="sub.id" :label="sub.subject" :value="sub.id" />
                </el-select>
                <el-button type="primary" @click="loadStudents">加载学生</el-button>
            </div>

            <!-- 学生列表 -->
            <div v-if="students.length === 0" class="empty-tip">
                请选择班级和科目，点击「加载学生」
            </div>
            <el-table v-else :data="students" border stripe>
                <el-table-column prop="name" label="姓名" />
                <el-table-column label="分数" width="150">
                    <template #default="{ row, $index }">
                        <el-input-number v-model="students[$index].score" :min="0" :max="100" :precision="1" step="0.5"
                            size="small" />
                    </template>
                </el-table-column>
            </el-table>

            <!-- 保存按钮 -->
            <div style="margin-top: 16px; text-align: right;">
                <el-button type="success" @click="saveScores">💾 保存成绩</el-button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()

const classList = ref([])
const subjectList = ref([])
const selectedClass = ref('')
const selectedSubject = ref('')
const students = ref([])

// 加载教师的班级列表
const loadClassList = async () => {
    try {
        const res = await request.get('/teacher/classes')
        if (res.data.code === 200) {
            classList.value = res.data.data || []
        }
    } catch {
        ElMessage.error('加载班级列表失败')
    }
}

// 加载科目列表
const loadSubjectList = async () => {
    try {
        const res = await request.get('/subjects/options')
        if (res.data.code === 200) {
            subjectList.value = res.data.data || []
        }
    } catch {
        ElMessage.error('加载科目列表失败')
    }
}

// 加载学生
const loadStudents = async () => {
    if (!selectedClass.value) {
        ElMessage.warning('请选择班级！')
        return
    }
    if (!selectedSubject.value) {
        ElMessage.warning('请选择科目！')
        return
    }

    try {
        const res = await request.get(`/students/by-class/${selectedClass.value}`)
        if (res.data.code === 200) {
            students.value = (res.data.data || []).map(s => ({ ...s, score: null }))
        }
    } catch {
        ElMessage.error('加载学生失败')
    }
}

// 保存成绩
const saveScores = async () => {
    const scores = students.value
        .filter(s => s.score !== null && s.score !== '')
        .map(s => ({
            student_id: s.id,
            score: s.score
        }))

    if (scores.length === 0) {
        ElMessage.warning('没有可保存的成绩')
        return
    }

    try {
        const res = await request.post('/scores/batch', {
            class_id: selectedClass.value,
            subject_id: selectedSubject.value,
            scores
        })
        if (res.data.code === 200) {
            ElMessage.success(res.data.message || '保存成功')
        } else {
            ElMessage.error(res.data.message || '保存失败')
        }
    } catch {
        ElMessage.error('保存失败')
    }
}

onMounted(() => {
    loadClassList()
    loadSubjectList()

    // 如果 URL 带了 classId，自动选中
    const classId = route.query.classId
    if (classId) {
        selectedClass.value = parseInt(classId)
        // 等班级列表加载完后再自动加载学生
        // 可以用 watch，但简单起见让用户手动点击加载
    }
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