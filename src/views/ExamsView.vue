<template>
    <div class="exams-container">
        <!-- 顶部操作栏 -->
        <div class="header">
            <h2>📝 考试管理</h2>
            <el-button type="primary" @click="openAddDialog">+ 添加考试</el-button>
        </div>

        <!-- 考试列表表格 -->
        <el-table :data="examList" stripe v-loading="loading" style="width: 100%; margin-top: 16px;">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="考试名称" />
            <el-table-column prop="created_at" label="创建时间" width="180">
                <template #default="{ row }">
                    {{ formatDateTime(row.created_at) }}
                </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                    <el-button size="small" type="danger" @click="handleDelete(row.id)">
                        删除
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>

    <!-- 添加考试弹窗 -->
    <el-dialog v-model="addDialogVisible" title="添加考试" width="400px">
        <el-form :model="addForm" label-width="80px">
            <el-form-item label="考试名称">
                <el-input v-model="addForm.name" placeholder="请输入考试名称，如：期中考试" />
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="addDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmAdd">确认</el-button>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

// 考试列表
const examList = ref([])
const loading = ref(false)

// 添加弹窗
const addDialogVisible = ref(false)
const addForm = reactive({
    name: ''
})

// 格式化时间
const formatDateTime = (value) => {
    if (!value) return ''
    const date = new Date(value)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 加载考试列表
const loadExams = async () => {
    loading.value = true
    try {
        const res = await request.get('/exams')
        if (res.data.code === 200) {
            examList.value = res.data.data || []
        } else {
            ElMessage.error(res.data.message || '加载失败')
        }
    } catch {
        ElMessage.error('加载考试列表失败')
    } finally {
        loading.value = false
    }
}

// 打开添加弹窗
const openAddDialog = () => {
    addForm.name = ''
    addDialogVisible.value = true
}

// 确认添加
const confirmAdd = async () => {
    if (!addForm.name.trim()) {
        ElMessage.warning('请输入考试名称')
        return
    }

    try {
        const res = await request.post('/exams', {
            name: addForm.name.trim()
        })
        if (res.data.code === 200) {
            ElMessage.success('添加成功')
            addDialogVisible.value = false
            loadExams()
        } else {
            ElMessage.error(res.data.message || '添加失败')
        }
    } catch {
        ElMessage.error('添加失败')
    }
}

// 删除考试
const handleDelete = (id) => {
    // 先确认是否有成绩关联
    ElMessageBox.confirm(
        '确定要删除该考试吗？\n⚠️ 如果该考试已有成绩数据，将无法删除。',
        '提示',
        {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning'
        }
    ).then(async () => {
        try {
            const res = await request.delete(`/exams/${id}`)
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadExams()
            } else {
                ElMessage.error(res.data.message || '删除失败')
            }
        } catch (error) {
            const msg = error.response?.data?.message || '删除失败'
            ElMessage.error(msg)
        }
    }).catch(() => { })
}

onMounted(() => {
    loadExams()
})
</script>

<style scoped>
.exams-container {
    padding: 20px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h2 {
    font-size: 20px;
    color: #1e2a3a;
    margin: 0;
}
</style>