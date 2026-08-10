<template>
    <div>
        <div class="page-title">📋 我的班级</div>
        <div class="content-card">
            <div v-if="loading" class="empty-tip">⏳ 加载中...</div>
            <div v-else-if="classList.length === 0" class="empty-tip">暂无绑定的班级</div>
            <ul v-else style="list-style: none; padding: 0;">
                <li v-for="cls in classList" :key="cls.id"
                    style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; border-bottom: 1px solid #eef2f6;">
                    <span>{{ cls.grade }}{{ cls.class }}班</span>
                    <div>
                        <el-button size="small" type="primary" @click="viewStudents(cls.id)">
                            查看学生
                        </el-button>
                        <el-button size="small" type="warning" @click="goToScoreEntry(cls.id)">
                            录入成绩
                        </el-button>
                    </div>
                </li>
            </ul>
        </div>

        <!-- 学生列表弹窗 -->
        <el-dialog v-model="studentDialogVisible" title="班级学生列表" width="700px">
            <el-table :data="studentList" border stripe>
                <el-table-column prop="id" label="ID" width="60" />
                <el-table-column prop="name" label="姓名" />
                <el-table-column label="性别" width="80">
                    <template #default="{ row }">
                        {{ row.gender === 1 ? '男' : '女' }}
                    </template>
                </el-table-column>
                <el-table-column prop="age" label="年龄" width="80" />
                <el-table-column prop="score" label="分数" width="80" />
            </el-table>
            <template #footer>
                <el-button @click="studentDialogVisible = false">关闭</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()

const classList = ref([])
const loading = ref(false)

const studentDialogVisible = ref(false)
const studentList = ref([])

// 加载我的班级
const loadMyClasses = async () => {
    loading.value = true
    try {
        const res = await request.get('/teacher/classes')
        if (res.data.code === 200) {
            classList.value = res.data.data || []
        }
    } catch {
        ElMessage.error('加载班级列表失败')
    } finally {
        loading.value = false
    }
}

// 查看学生
const viewStudents = async (classId) => {
    try {
        const res = await request.get(`/students/by-class/${classId}`)
        if (res.data.code === 200) {
            studentList.value = res.data.data || []
            studentDialogVisible.value = true
        }
    } catch {
        ElMessage.error('加载学生列表失败')
    }
}

// 跳转到成绩录入（带班级参数）
const goToScoreEntry = (classId) => {
    router.push(`/teacher/score-entry?classId=${classId}`)
}

onMounted(() => {
    loadMyClasses()
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