<template>
    <div class="main-content">
        <!-- 搜索栏 -->
        <div class="filter-bar">
            <el-input v-model="searchKeyword" placeholder="搜索科目名称..." clearable size="large"
                style="flex: 1; min-width: 150px;" @keyup.enter="handleSearch" @clear="handleSearch" />
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
            <el-button type="success" @click="openAddDialog">添加科目</el-button>
        </div>

        <!-- 表格 -->
        <el-table :data="subjectList" stripe row-height="120"
            style="width: 100%;  font-size: 15px; margin-top: 12px;border-radius: 6px; overflow: hidden;border-bottom: 1px solid #e0e0e0;"
            height="600" v-loading="loading" :cell-style="{ textAlign: 'left' }">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="subject" label="科目" />
            <el-table-column prop="full_score" label="满分" />
            <el-table-column label="是否特殊科目">
                <template #default="{ row }">
                    <el-tag :type="row.is_class_special ? 'warning' : 'info'">
                        {{ row.is_class_special ? '是' : '否' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="class_names" label="所属班级" />
            <el-table-column label="操作" fixed="right">
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
        <el-dialog v-model="addDialogVisible" title="添加科目" width="480px">
            <el-form :model="addForm" label-width="100px">
                <el-form-item label="科目名称">
                    <el-input v-model="addForm.name" placeholder="请输入科目名称" />
                </el-form-item>
                <el-form-item label="满分分数">
                    <el-input-number v-model="addForm.fullScore" :min="0" :max="300" :precision="1" step="0.5" />
                </el-form-item>
                <el-form-item label="是否特殊科目">
                    <el-switch v-model="addForm.isSpecial" active-text="是" inactive-text="否" />
                </el-form-item>
                <el-form-item label="所属班级">
                    <el-select v-model="addForm.classIds" multiple collapse-tags collapse-tags-tooltip
                        placeholder="请选择班级（不选默认为全校）" style="width: 100%;">
                        <el-option label="全校" value="" />
                        <el-option v-for="cls in classList" :key="cls.id" :label="cls.grade + cls.class + '班'"
                            :value="cls.id" />
                    </el-select>
                    <div style="font-size: 12px; color: #999; margin-top: 4px;">
                        不选任何班级表示该科目为全校科目
                    </div>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="addDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmAdd">确认</el-button>
            </template>
        </el-dialog>

        <!-- 编辑弹窗 -->
        <el-dialog v-model="editDialogVisible" title="编辑科目" width="480px">
            <el-form :model="editForm" label-width="100px">
                <el-form-item label="科目名称">
                    <el-input v-model="editForm.name" placeholder="请输入科目名称" />
                </el-form-item>
                <el-form-item label="满分分数">
                    <el-input-number v-model="editForm.fullScore" :min="0" :max="300" :precision="1" step="0.5" />
                </el-form-item>
                <el-form-item label="是否特殊科目">
                    <el-switch v-model="editForm.isSpecial" active-text="是" inactive-text="否" />
                </el-form-item>
                <el-form-item label="所属班级">
                    <el-select v-model="editForm.classIds" multiple collapse-tags collapse-tags-tooltip
                        placeholder="请选择班级（不选默认为全校）" style="width: 100%;">
                        <el-option label="全校" value="" />
                        <el-option v-for="cls in classList" :key="cls.id" :label="cls.grade + cls.class + '班'"
                            :value="cls.id" />
                    </el-select>
                    <div style="font-size: 12px; color: #999; margin-top: 4px;">
                        不选任何班级表示该科目为全校科目
                    </div>
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
const subjectList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)

// 搜索
const searchKeyword = ref('')

// 班级列表
const classList = ref([])

// 添加弹窗
const addDialogVisible = ref(false)
const addForm = reactive({
    name: '',
    fullScore: 100,
    isSpecial: false,
    classIds: []  // 空数组表示全校
})

// 编辑弹窗
const editDialogVisible = ref(false)
const editForm = reactive({
    id: null,
    name: '',
    fullScore: 100,
    isSpecial: false,
    classIds: []
})

// 加载班级列表
const loadClassList = async () => {
    try {
        const res = await request.get('/classes/options')
        if (res.data.code === 200) {
            classList.value = res.data.data
        }
    } catch {
        console.log('加载班级列表失败')
    }
}

// 加载数据
const loadData = async () => {
    loading.value = true
    try {
        const params = {
            page: currentPage.value,
            limit: pageSize.value,
            search: searchKeyword.value
        }
        const res = await request.get('/subjects', { params })
        if (res.data.code === 200) {
            subjectList.value = res.data.data
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
    addForm.name = ''
    addForm.fullScore = 100
    addForm.isSpecial = false
    addForm.classIds = []
    addDialogVisible.value = true
}

// 确认添加
const confirmAdd = async () => {
    // 基础校验
    if (!addForm.name.trim()) {
        ElMessage.warning('请输入科目名称')
        return
    }
    if (addForm.fullScore <= 0) {
        ElMessage.warning('满分必须大于0')
        return
    }

    try {
        const payload = {
            name: addForm.name,
            full_score: addForm.fullScore,
            is_special: addForm.isSpecial ? 1 : 0,
            class_ids: addForm.classIds || []  // 空数组表示全校
        }
        const res = await request.post('/subjects', payload)
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
        const res = await request.get(`/subjects/${row.id}`)
        if (res.data.code === 200) {
            const data = res.data.data
            editForm.id = data.id
            editForm.name = data.subject
            editForm.fullScore = data.full_score
            editForm.isSpecial = data.is_class_special === 1
            editForm.classIds = data.class_ids || []
            editDialogVisible.value = true
        }
    } catch (error) {
        ElMessage.error('获取科目信息失败')
    }
}

// 确认编辑
const confirmEdit = async () => {
    if (!editForm.name.trim()) {
        ElMessage.warning('请输入科目名称')
        return
    }
    if (editForm.fullScore <= 0) {
        ElMessage.warning('满分必须大于0')
        return
    }

    try {
        const payload = {
            subject: editForm.name,
            full_score: editForm.fullScore,
            is_special: editForm.isSpecial ? 1 : 0,
            class_ids: editForm.classIds || []
        }
        const res = await request.put(`/subjects/${editForm.id}`, payload)
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
    ElMessageBox.confirm('确定要删除该科目吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(async () => {
        try {
            const res = await request.delete(`/subjects/${id}`)
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
    loadClassList()
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