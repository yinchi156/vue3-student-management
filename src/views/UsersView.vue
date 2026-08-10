<template>
    <div class="main-content">
        <!-- 搜索栏 -->
        <div class="filter-bar">
            <el-input v-model="searchKeyword" placeholder="搜索用户名..." clearable size="large"
                style="flex: 1; min-width: 150px;" @keyup.enter="handleSearch" @clear="handleSearch" />
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
        </div>

        <!-- 表格 -->
        <el-table :data="userList" stripe row-height="120"
            style="width: 100%;  font-size: 15px; margin-top: 12px;border-radius: 6px; overflow: hidden;border-bottom: 1px solid #e0e0e0;"
            height="600" v-loading="loading" :cell-style="{ textAlign: 'left' }">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column label="身份">
                <template #default="{ row }">
                    <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'teacher' ? 'warning' : 'info'">
                        {{ roleMap[row.role] || row.role }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right">
                <template #default="{ row }">
                    <el-select v-model="row.role" size="small" style="width: 90px; margin-right: 8px;"
                        @change="handleRoleChange(row)">
                        <el-option label="学生" value="user" />
                        <el-option label="教师" value="teacher" />
                        <el-option label="管理员" value="admin" />
                    </el-select>
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
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

// 表格数据
const userList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)

// 搜索
const searchKeyword = ref('')

// 角色映射
const roleMap = {
    user: '学生',
    teacher: '教师',
    admin: '管理员'
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