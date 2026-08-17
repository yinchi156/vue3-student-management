<template>
    <div class="exams-container">
        <!-- 顶部操作栏 -->
        <div class="header">
            <h2>📝 考试管理</h2>
            <el-button type="primary" @click="openAddDialog">+ 添加考试</el-button>
        </div>

        <!-- 考试列表表格 -->
        <el-table :data="examList" stripe v-loading="loading" style="width: 100%; margin-top: 16px;">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="name" label="考试名称" width="180" />
            <el-table-column prop="student_count" label="考生人数" width="120" />
            <el-table-column prop="total_full_score" label="满分" width="120" />
            <el-table-column prop="teacher_names" label="监考员" />
            <el-table-column prop="created_at" label="考试时间" width="180">
                <template #default="{ row }">
                    {{ formatDateTime(row.created_at) }}
                </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                    <el-button size="small" type="primary" @click="openEditDialog(row)">
                        编辑
                    </el-button>
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
            <el-form-item label="监考员">
                <el-select v-model="addForm.teachers" multiple collapse-tags collapse-tags-tooltip placeholder="请选择监考员"
                    style="width: 100%;">

                    <el-option v-for="tea in teacherList" :key="tea.id" :label="tea.username" :value="tea.id" />
                </el-select>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="addDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmAdd">确认</el-button>
        </template>
    </el-dialog>
    <!-- 编辑考试弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑考试" width="400px">
        <el-form :model="editForm" label-width="80px">
            <el-form-item label="考试名称">
                <el-input v-model="editForm.name" placeholder="请输入考试名称，如：期中考试" />
            </el-form-item>
            <el-form-item label="监考员">
                <el-select v-model="editForm.teachers" multiple collapse-tags collapse-tags-tooltip placeholder="请选择监考员"
                    style="width: 100%;">

                    <el-option v-for="teacher in teacherList" :key="teacher.id" :label="teacher.username"
                        :value="teacher.id" />
                </el-select>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmEdit">确认</el-button>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { id } from 'element-plus/es/locales.mjs'

// 考试列表
const examList = ref([])
const loading = ref(false)
const teacherList = ref([])

// 添加弹窗
const addDialogVisible = ref(false)
const editDialogVisible = ref(false)
const addForm = reactive({
    name: '',
    teachers: []
})
const editForm = reactive({
    id: null,
    name: '',
    teachers: []
})

// 格式化时间
const formatDateTime = (value) => {
    if (!value) return ''
    const date = new Date(value)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
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

const loadteacherList = async () => {
    try {
        const res = await request.get('/loadteachers')
        if (res.data.code === 200) {
            teacherList.value = res.data.data || []
        } else {
            ElMessage.error(res.data.message || '加载失败')
        }

    } catch {
        ElMessage.error('加载教师列表失败')
    }
}

// 打开添加弹窗
const openAddDialog = () => {
    addForm.name = ''
    addForm.teachers = []
    addDialogVisible.value = true
}

// 打开编辑弹窗
const openEditDialog = (row) => {
    editForm.id = row.id
    editForm.name = row.name
    editForm.teachers = row.teacher_ids.map(Number)  // 转成数字
    editDialogVisible.value = true
}

// 确认添加
const confirmAdd = async () => {
    if (!addForm.name.trim()) {
        ElMessage.warning('请输入考试名称')
        return
    }

    try {
        const res = await request.post('/exams', {
            name: addForm.name.trim(),
            teachers: addForm.teachers
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

//编辑考试
const confirmEdit = async () => {
    if (!editForm.name.trim()) {
        ElMessage.warning('请输入考试名称')
        return
    }

    try {
        const res = await request.put(`/exams/${editForm.id}`, {
            name: editForm.name.trim(),
            teachers: editForm.teachers
        })
        if (res.data.code === 200) {
            ElMessage.success('修改成功')
            editDialogVisible.value = false
            loadExams()
        } else {
            ElMessage.error(res.data.message || '修改失败')
        }
    } catch {
        ElMessage.error('修改失败')
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
    loadteacherList()
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