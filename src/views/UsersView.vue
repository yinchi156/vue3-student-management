<template>
    <div class="main-content">
        <!-- 搜索栏 -->
        <div class="filter-bar">
            <el-input v-model="searchKeyword" placeholder="搜索用户名..." clearable size="large"
                style="flex: 1; min-width: 150px;" @keyup.enter="handleSearch" @clear="handleSearch" />
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
            <el-button type="success" @click="openAddDialog">添加教师</el-button>
        </div>

        <!-- 表格 -->
        <el-table :data="userList" stripe row-height="120"
            style="width: 100%;  font-size: 15px; margin-top: 12px;border-radius: 6px; overflow: hidden;border-bottom: 1px solid #e0e0e0;"
            height="600" v-loading="loading" :cell-style="{ textAlign: 'left' }">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="姓名" />
            <el-table-column prop="role" label="身份" width="100">
                <template #default="{ row }">
                    <span v-if="row.role === 'teacher' && row.is_class_teacher === 1">班主任</span>
                    <span v-else-if="row.role === 'teacher'">教师</span>
                    <span v-else>{{ row.role }}</span>
                </template>
            </el-table-column>
            <el-table-column prop="subjects" label="任课科目" />
            <el-table-column prop="classes" label="所授班级" />
            <el-table-column label="操作" fixed="right">
                <template #default="{ row }">
                    <el-button size="small" type="primary" @click="openEditDialog(row)">
                        编辑
                    </el-button>
                    <el-button size="small" type="warning" @click="handleResetPassword(row)">
                        重置密码
                    </el-button>
                    <el-button size="small" type="danger" @click="handleDelete(row)">
                        删除
                    </el-button>
                </template>
            </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
                :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="handlePageSizeChange"
                @current-change="handlePageChange" />
        </div>

        <!-- 添加教师弹窗 -->
        <el-dialog v-model="addDialogVisible" title="添加教师" width="500px">
            <el-form :model="addForm" label-width="100px">
                <!-- 教师姓名 -->
                <el-form-item label="教师姓名">
                    <el-input v-model="addForm.username" placeholder="请输入教师姓名" />
                </el-form-item>

                <!-- 所教班级（多选） -->
                <el-form-item label="所教班级">
                    <el-select v-model="addForm.class_ids" multiple collapse-tags collapse-tags-tooltip
                        placeholder="请选择班级" style="width: 100%;">
                        <el-option v-for="cls in classList" :key="cls.id" :label="cls.grade + cls.class + '班'"
                            :value="cls.id" />
                    </el-select>
                </el-form-item>

                <!-- 所教科目（单选） -->
                <el-form-item label="所教科目">
                    <el-select v-model="addForm.subject_id" placeholder="请选择科目" style="width: 100%;">
                        <el-option v-for="sub in subjectList" :key="sub.id" :label="sub.subject" :value="sub.id" />
                    </el-select>
                </el-form-item>

                <!-- 是否为班主任（开关） -->
                <el-form-item label="是否为班主任">
                    <el-switch v-model="addForm.is_class_teacher" active-text="是" inactive-text="否" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="addDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmAdd">确认</el-button>
            </template>
        </el-dialog>

        <!-- 编辑教师弹窗 -->
        <el-dialog v-model="editDialogVisible" title="添加教师" width="500px">
            <el-form :model="editForm" label-width="100px">
                <!-- 教师姓名 -->
                <el-form-item label="教师姓名">
                    <el-input v-model="editForm.username" placeholder="请输入教师姓名" />
                </el-form-item>

                <!-- 所教班级（多选） -->
                <el-form-item label="所教班级">
                    <el-select v-model="editForm.class_ids" multiple collapse-tags collapse-tags-tooltip
                        placeholder="请选择班级" style="width: 100%;">
                        <el-option v-for="cls in classList" :key="cls.id" :label="cls.grade + cls.class + '班'"
                            :value="cls.id" />
                    </el-select>
                </el-form-item>

                <!-- 所教科目（单选） -->
                <el-form-item label="所教科目">
                    <el-select v-model="editForm.subject_id" placeholder="请选择科目" style="width: 100%;">
                        <el-option v-for="sub in subjectList" :key="sub.id" :label="sub.subject" :value="sub.id" />
                    </el-select>
                </el-form-item>

                <!-- 是否为班主任（开关） -->
                <el-form-item label="是否为班主任">
                    <el-switch v-model="editForm.is_class_teacher" active-text="是" inactive-text="否" :active-value="1"
                        :inactive-value="0" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="editDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmedit">确认</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { number } from 'echarts'
import { id } from 'element-plus/es/locales.mjs'

// 表格数据
const userList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)


// 搜索
const searchKeyword = ref('')

// 弹窗控制
const addDialogVisible = ref(false)
const editDialogVisible = ref(false)

// 角色映射
const roleMap = {
    user: '学生',
    teacher: '教师',
    admin: '管理员'
}

const addForm = reactive({
    username: '',
    class_ids: [],      // 多选，数组
    subject_id: null,   // 单选
    is_class_teacher: false
})

const editForm = reactive({
    id: null,
    username: '',
    class_ids: [],      // 多选，数组
    subject_id: null,   // 单选
    is_class_teacher: false
})

// 班级列表
const classList = ref([])

// 科目列表
const subjectList = ref([])

// 加载数据
const loadData = async () => {
    loading.value = true
    try {
        const params = {
            page: currentPage.value,
            limit: pageSize.value,
            search: searchKeyword.value
        }
        const res = await request.get('/users', { params })
        if (res.data.code === 200) {
            userList.value = res.data.data
            total.value = res.data.total
        }
    } catch (error) {
        ElMessage.error('加载数据失败')
    } finally {
        loading.value = false
    }
}

// 加载班级列表
const loadClassList = async () => {
    try {
        const res = await request.get('/classes/options')
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


// 打开弹窗
const openAddDialog = () => {
    addForm.username = ''
    addForm.class_ids = []
    addForm.subject_id = null
    addForm.is_class_teacher = false
    addDialogVisible.value = true
}

// 确认添加
const confirmAdd = async () => {
    if (!addForm.username.trim()) {
        ElMessage.warning('请输入教师姓名')
        return
    }
    if (addForm.class_ids.length === 0) {
        ElMessage.warning('请至少选择一个班级')
        return
    }
    if (!addForm.subject_id) {
        ElMessage.warning('请选择所教科目')
        return
    }

    try {
        const res = await request.post('/teachers', {
            username: addForm.username.trim(),
            class_ids: addForm.class_ids,
            subject_id: addForm.subject_id,
            is_class_teacher: addForm.is_class_teacher ? 1 : 0
        })
        if (res.data.code === 200) {
            ElMessage.success('添加成功')
            addDialogVisible.value = false
            loadData()  // 刷新教师列表
        } else {
            ElMessage.error(res.data.message || '添加失败')
        }
    } catch (error) {
        const msg = error.response?.data?.message || '添加失败'
        ElMessage.error(msg)
    }
}

const openEditDialog = async (row) => {
    const res = await request.get(`/users/${row.id}`)
    const data = res.data.data
    editForm.id = data.id
    editForm.username = data.username
    editForm.class_ids = data.class_ids   // [1, 2, 3]
    editForm.subject_id = Number(data.subject_ids[0]) //后端返回的是数组
    editForm.is_class_teacher = data.is_class_teacher
    editDialogVisible.value = true
}

const confirmedit = async () => {
    // 校验
    if (!editForm.username.trim()) {
        ElMessage.warning('请输入教师姓名')
        return
    }
    if (editForm.class_ids.length === 0) {
        ElMessage.warning('请至少选择一个班级')
        return
    }
    if (!editForm.subject_id) {
        ElMessage.warning('请选择所教科目')
        return
    }

    try {
        const payload = {
            username: editForm.username.trim(),
            is_class_teacher: editForm.is_class_teacher ? 1 : 0,
            subject_ids: editForm.subject_id ? [editForm.subject_id] : [],  // 单值转数组
            class_ids: editForm.class_ids  // 已经是数组
        }

        const res = await request.put(`/users/${editForm.id}`, payload)
        if (res.data.code === 200) {
            ElMessage.success('修改成功')
            editDialogVisible.value = false
            loadData()  // 刷新列表
        } else {
            ElMessage.error(res.data.message || '修改失败')
        }
    } catch (error) {
        const msg = error.response?.data?.message || '修改失败'
        ElMessage.error(msg)
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

// 角色修改
const handleRoleChange = (row) => {
    const newRole = row.role
    const roleDisplay = roleMap[newRole] || newRole

    ElMessageBox.confirm(
        `确定要将用户「${row.username}」的角色改为「${roleDisplay}」吗？`,
        '修改角色',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }
    ).then(async () => {
        try {
            const res = await request.put(`/users/${row.id}/role`, { role: newRole })
            if (res.data.code === 200) {
                ElMessage.success('角色修改成功')
                loadData()
            } else {
                ElMessage.error(res.data.message || '修改失败')
                // 恢复原角色（需要重新加载）
                loadData()
            }
        } catch (error) {
            const msg = error.response?.data?.message || '修改失败'
            ElMessage.error(msg)
            loadData()
        }
    }).catch(() => {
        // 用户取消，重新加载恢复显示
        loadData()
    })
}

// 重置密码
const handleResetPassword = (row) => {
    ElMessageBox.confirm(
        `确定要重置用户「${row.username}」的密码吗？\n重置后密码为默认密码（123456）`,
        '重置密码',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }
    ).then(async () => {
        try {
            const res = await request.put(`/users/${row.id}/reset-password`)
            if (res.data.code === 200) {
                ElMessage.success(res.data.message || '重置成功')
                loadData()
            } else {
                ElMessage.error(res.data.message || '重置失败')
            }
        } catch (error) {
            const msg = error.response?.data?.message || '重置失败'
            ElMessage.error(msg)
        }
    }).catch(() => { })
}

// 删除用户
const handleDelete = (row) => {
    ElMessageBox.confirm(
        `确定要删除用户「${row.username}」吗？\n⚠️ 删除后不可恢复！`,
        '删除用户',
        {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'error'
        }
    ).then(async () => {
        try {
            const res = await request.delete(`/users/${row.id}`)
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            } else {
                ElMessage.error(res.data.message || '删除失败')
            }
        } catch (error) {
            const msg = error.response?.data?.message || '删除失败'
            ElMessage.error(msg)
        }
    }).catch(() => { })
}

// 初始化
onMounted(() => {
    loadClassList()
    loadSubjectList()
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