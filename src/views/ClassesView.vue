<template>
    <div class="main-content">
        <!-- 搜索栏 -->
        <div class="filter-bar">

            <el-input v-model="searchKeyword" placeholder="搜索年级或班级名称..." clearable style="flex: 1; min-width: 150px;"
                size="large" @keyup.enter="handleSearch" @clear="handleSearch" />
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
            <el-button type="success" @click="openAddDialog">添加班级</el-button>
        </div>

        <!-- 表格 -->
        <el-table :data="classList" stripe row-height="120"
            style="width: 100%;  font-size: 15px; margin-top: 12px;border-radius: 6px; overflow: hidden;border-bottom: 1px solid #e0e0e0;"
            height="600" v-loading="loading" :cell-style="{ textAlign: 'left' }">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="grade" label="年级" />
            <el-table-column label="班级">
                <template #default="{ row }">
                    {{ row.class }}班
                </template>
            </el-table-column>
            <el-table-column prop="student_count" label="班级人数" />
            <el-table-column label="是否重点班">
                <template #default="{ row }">
                    <el-tag :type="row.is_key_class ? 'success' : 'info'">
                        {{ row.is_key_class ? '是' : '否' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="avg_score" label="学生平均分" />
            <el-table-column label="操作" fixed="right" align="center">
                <template #default="{ row }">
                    <el-button size="small" type="primary" @click="openEditDialog(row)">编辑</el-button>
                    <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
                :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="handlePageSizeChange"
                @current-change="handlePageChange" />
        </div>

        <!-- 添加弹窗 -->
        <el-dialog v-model="addDialogVisible" title="添加班级" width="420px">
            <el-form :model="addForm" label-width="80px">
                <el-form-item label="年级">
                    <el-radio-group v-model="addForm.grade">
                        <el-radio label="高一">高一</el-radio>
                        <el-radio label="高二">高二</el-radio>
                        <el-radio label="高三">高三</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="班级编号">
                    <el-input-number v-model="addForm.classNumber" :min="1" :max="30" placeholder="请输入班级编号" />
                </el-form-item>
                <el-form-item label="是否重点班">
                    <el-switch v-model="addForm.isKeyClass" active-text="是" inactive-text="否" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="addDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmAdd">确认</el-button>
            </template>
        </el-dialog>

        <!-- 编辑弹窗 -->
        <el-dialog v-model="editDialogVisible" title="编辑班级" width="420px">
            <el-form :model="editForm" label-width="80px">
                <el-form-item label="年级">
                    <el-radio-group v-model="editForm.grade">
                        <el-radio label="高一">高一</el-radio>
                        <el-radio label="高二">高二</el-radio>
                        <el-radio label="高三">高三</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="班级编号">
                    <el-input-number v-model="editForm.classNumber" :min="1" :max="30" placeholder="请输入班级编号" />
                </el-form-item>
                <el-form-item label="是否重点班">
                    <el-switch v-model="editForm.isKeyClass" active-text="是" inactive-text="否" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="editDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmEdit">确认</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import request from '@/utils/request'

// 表格数据
const classList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)

// 搜索
const searchKeyword = ref('')

// 添加弹窗
const addDialogVisible = ref(false)
const addForm = reactive({
    grade: '高一',
    classNumber: 1,
    isKeyClass: false
})

// 编辑弹窗
const editDialogVisible = ref(false)
const editForm = reactive({
    id: null,
    grade: '高一',
    classNumber: 1,
    isKeyClass: false
})

// 加载数据
const loadData = async () => {
    loading.value = true
    try {
        const params = {
            page: currentPage.value,
            limit: pageSize.value,
            search: searchKeyword.value
        }
        const res = await request.get('/classes', { params })
        if (res.data.code === 200) {
            classList.value = res.data.data
            total.value = res.data.total
        }
    } catch (error) {
        ElMessage.error('加载数据失败')
    } finally {
        loading.value = false
    }
}

// 搜索
const handleSearch = () => {
    currentPage.value = 1
    loadData()
}

// 重置搜索
const resetSearch = () => {
    searchKeyword.value = ''
    currentPage.value = 1
    loadData()
}

// 分页变化
const handlePageChange = (page) => {
    currentPage.value = page
    loadData()
}

const handlePageSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
    loadData()
}

// 打开添加弹窗
const openAddDialog = () => {
    addForm.grade = '高一'
    addForm.classNumber = 1
    addForm.isKeyClass = false
    addDialogVisible.value = true
}

// 确认添加
const confirmAdd = async () => {
    try {
        const payload = {
            grade: addForm.grade,
            class: addForm.classNumber,
            is_key_class: addForm.isKeyClass ? 1 : 0
        }
        const res = await request.post('/classes', payload)
        if (res.data.code === 200) {
            ElMessage.success('添加成功')
            addDialogVisible.value = false
            loadData()
        } else {
            ElMessage.error(res.data.message || '添加失败')
        }
    } catch (error) {
        const msg = error.response?.data?.message || '添加失败'
        ElMessage.error(msg)
    }
}

// 打开编辑弹窗
const openEditDialog = async (row) => {
    try {
        const res = await request.get(`/classes/${row.id}`)
        if (res.data.code === 200) {
            const data = res.data.data
            editForm.id = data.id
            editForm.grade = data.grade
            editForm.classNumber = data.class_number
            editForm.isKeyClass = data.is_key_class === 1
            editDialogVisible.value = true
        }
    } catch (error) {
        ElMessage.error('获取班级信息失败')
    }
}

// 确认编辑
const confirmEdit = async () => {
    try {
        const payload = {
            grade: editForm.grade,
            class_number: editForm.classNumber,
            is_key_class: editForm.isKeyClass ? 1 : 0
        }
        const res = await request.put(`/classes/${editForm.id}`, payload)
        if (res.data.code === 200) {
            ElMessage.success('修改成功')
            editDialogVisible.value = false
            loadData()
        } else {
            ElMessage.error(res.data.message || '修改失败')
        }
    } catch (error) {
        const msg = error.response?.data?.message || '修改失败'
        ElMessage.error(msg)
    }
}

// 删除
const handleDelete = (id) => {
    ElMessageBox.confirm('确定要删除该班级吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(async () => {
        try {
            const res = await request.delete(`/classes/${id}`)
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            } else {
                ElMessage.error(res.data.message || '删除失败')
            }
        } catch (error) {
            ElMessage.error('删除失败')
        }
    }).catch(() => { })
}

// 初始化
onMounted(() => {
    loadData()
})
</script>

<style scoped>
.main-content {
    padding: 16px;
}

.filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    background: #fff;
    padding: 12px 16px;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
}

:deep(.el-table .cell) {
    padding: 0 12px !important;
    line-height: 40px !important;
}
</style>