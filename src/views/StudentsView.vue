<template>
    <div class="main-content">
        <!-- 搜索筛选栏 -->
        <div class="filter-bar">
            <!-- 性别筛选 -->
            <el-checkbox-group v-model="genderFilter" class="gender-group" size="large"
                @change="handleGenderFilterChange">
                <el-checkbox :label="1" value="1">男</el-checkbox>
                <el-checkbox :label="0" value="0">女</el-checkbox>
            </el-checkbox-group>
            <el-select v-model="selectedFields" size="large" multiple collapse-tags collapse-tags-tooltip
                placeholder="筛选字段" style="width: 180px;">
                <el-option label="姓名" value="name" />
                <el-option label="班级" value="class" />
                <el-option label="年龄" value="age" />
                <el-option label="分数" value="score" />
            </el-select>
            <el-input v-model="searchKeyword" placeholder="输入关键词搜索..." clearable style="flex: 1; min-width: 150px;"
                size="large" @keyup.enter="handleSearch" @clear="handleSearch" />

            <el-date-picker v-model="dateRange" size="large" type="daterange" range-separator="至"
                start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="max-width: 220px;" />

            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
            <el-button type="success" @click="openAddDialog">添加学生</el-button>
        </div>

        <!-- 表格 -->
        <div style="border-radius:6px; overflow: hidden;">
            <el-table :data="studentList" stripe row-height="120"
                style="width: 100%;  font-size: 15px; margin-top: 12px;border-radius: 6px; overflow: hidden;border-bottom: 1px solid #e0e0e0;"
                height="600" v-loading="loading" :cell-style="{ textAlign: 'left' }">
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="name" label="姓名" />
                <el-table-column prop="gender" label="性别">
                    <template #default="{ row }">
                        {{ row.gender === 1 ? '男' : '女' }}
                    </template>
                </el-table-column>
                <el-table-column prop="age" label="年龄" />
                <el-table-column prop="class" label="班级">
                    <template #default="{ row }">
                        {{ row.class }}班
                    </template>
                </el-table-column>
                <el-table-column prop="score" label="分数" />
                <el-table-column prop="createTime" label="创建时间">
                    <template #default="{ row }">
                        {{ formatDateTime(row.createTime) }}
                    </template>
                </el-table-column>
                <el-table-column label="操作" fixed="right">
                    <template #default="{ row }">
                        <el-button size="small" type="primary" @click="openEditDialog(row)">编辑</el-button>
                        <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
                :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="handlePageSizeChange"
                @current-change="handlePageChange" />
        </div>

        <!-- 添加弹窗 -->
        <el-dialog v-model="addDialogVisible" title="添加学生" width="400px">
            <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="60px">
                <el-form-item label="姓名" prop="name">
                    <el-input v-model="addForm.name" placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item label="性别" prop="gender">
                    <el-radio-group v-model="addForm.gender">
                        <el-radio :label="1">男</el-radio>
                        <el-radio :label="0">女</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="年龄" prop="age">
                    <el-input v-model="addForm.age" placeholder="请输入年龄" :min="1" :max="100" />
                </el-form-item>
                <el-form-item label="班级" prop="class_id">
                    <el-select v-model="addForm.class_id" placeholder="请选择班级">
                        <el-option v-for="cls in classList" :key="cls.id" :label="cls.grade + cls.class + '班'"
                            :value="cls.id" />
                    </el-select>
                </el-form-item>
                <el-form-item label="分数" prop="score">
                    <el-input v-model="addForm.score" placeholder="请输入分数" :min="0" :max="750" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="addDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmAdd">确认</el-button>
            </template>
        </el-dialog>

        <!-- 编辑弹窗 -->
        <el-dialog v-model="editDialogVisible" title="修改学生" width="400px">
            <el-form :model="editForm" :rules="editRules" label-width="60px">
                <el-form-item label="姓名">
                    <el-input v-model="editForm.name" placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item label="性别">
                    <el-radio-group v-model="editForm.gender">
                        <el-radio :label="1">男</el-radio>
                        <el-radio :label="0">女</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="年龄">
                    <el-input v-model="editForm.age" :min="1" :max="100" />
                </el-form-item>
                <el-form-item label="班级">
                    <el-select v-model="editForm.class_id" placeholder="请选择班级">
                        <el-option v-for="cls in classList" :key="cls.id" :label="cls.grade + cls.class + '班'"
                            :value="cls.id" />
                    </el-select>
                </el-form-item>
                <el-form-item label="分数">
                    <el-input v-model="editForm.score" :min="0" :max="750" />
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
import { Search } from '@element-plus/icons-vue'
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'

// 表格数据
const studentList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const route = useRoute()
const router = useRouter()

// 搜索条件
// 默认选中姓名和班级
const selectedFields = ref(['name',])
const searchKeyword = ref('')
const genderFilter = ref([])
const dateRange = ref([])

// 班级列表
const classList = ref([])

// 添加弹窗
const addDialogVisible = ref(false)
const addFormRef = ref(null)
//添加提示弹窗
const addRules = {
    name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
    ],
    gender: [
        { required: true, message: '请选择性别', trigger: 'change' }
    ],
    age: [
        { required: true, message: '请输入年龄', trigger: 'blur' },
    ],
    class_id: [
        { required: true, message: '请选择班级', trigger: 'change' }
    ],
    score: [
        { required: true, message: '请输入分数', trigger: 'blur' },
    ]
}

const addForm = reactive({
    name: '',
    gender: null,
    age: '',
    class_id: '',
    score: ''
})

// 编辑弹窗
const editDialogVisible = ref(false)
const editForm = reactive({
    id: null,
    name: '',
    gender: 1,
    age: 18,
    class_id: null,
    score: 60
})

// 格式化日期
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

// 加载数据
const loadData = async () => {
    loading.value = true

    try {

        const params = {
            page: currentPage.value,
            limit: pageSize.value,
            search: searchKeyword.value,
            fields: selectedFields.value.length > 0 ? selectedFields.value : ['name'],
            gender: genderFilter.value.join(','),
            start_date: dateRange.value?.[0] || '',
            end_date: dateRange.value?.[1] || ''
        }
        const res = await request.get(`/students`, { params })
        if (res.data.code === 200) {
            studentList.value = res.data.data
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
        const res = await request.get(`/classes/options`)
        if (res.data.code === 200) {
            classList.value = res.data.data//返回班级列表
        }
    } catch {
        // 忽略班级加载失败
    }
}

//男女筛选搜索
const handleGenderFilterChange = (val) => {
    console.log('性别筛选变化:', val)
    // 判断如果数组长度大于1，则只保留最后一个选中的值
    if (val.length > 1) {
        genderFilter.value = [val[val.length - 1]]//数组取后一个
    }
    currentPage.value = 1
    loadData()
}

// 搜索
const handleSearch = () => {

    currentPage.value = 1

    loadData()
}

// 统一更新 URL 的函数
const updateURL = () => {
    const query = {
        page: currentPage.value,
        keyword: searchKeyword.value,
        gender: genderFilter.value.join(','),
        start_date: dateRange.value?.[0] || '',
        end_date: dateRange.value?.[1] || ''
    }
    // 删除空参数
    Object.keys(query).forEach(key => {
        if (!query[key]) delete query[key]
    })
    router.push({ query })
}

// 重置搜索
const resetSearch = () => {
    searchKeyword.value = ''
    genderFilter.value = []
    dateRange.value = []
    currentPage.value = 1
    loadData()
    updateURL()
}

// 分页变化
const handlePageChange = (page) => {
    currentPage.value = page
    updateURL()
    loadData()
}

const handlePageSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
    updateURL()
    loadData()
}

// 打开添加弹窗
const openAddDialog = () => {
    addFormRef.value?.resetFields()
    addDialogVisible.value = true
}

// 确认添加
const confirmAdd = async () => {
    const valid = await addFormRef.value.validate().catch(() => false)
    if (!valid) return
    try {
        const res = await request.post(`/students`, addForm)
        if (res.data.code === 200) {
            ElMessage.success('添加成功')
            addDialogVisible.value = false
            loadData()
        }
    } catch (error) {
        const msg = error.response?.data?.message || '添加失败'
        ElMessage.error(msg)
    }
}

// 打开编辑弹窗
const openEditDialog = async (row) => {
    try {
        const res = await request.get(`/students/${row.id}`)
        if (res.data.code === 200) {
            const data = res.data.data
            editForm.id = data.id
            editForm.name = data.name
            editForm.gender = data.gender
            editForm.age = data.age
            editForm.class_id = data.class_id  // 本来就是数字，不用转
            editForm.score = data.score
            editDialogVisible.value = true
        }
    } catch {
        ElMessage.error('获取学生信息失败')
    }
}

// 确认编辑
const confirmEdit = async () => {
    try {
        const res = await request.put(
            `/students/${editForm.id}`,
            editForm
        )
        if (res.data.code === 200) {
            ElMessage.success('修改成功')
            editDialogVisible.value = false
            loadData()
        }
    } catch (error) {
        const msg = error.response?.data?.message || '修改失败'
        ElMessage.error(msg)
    }
}

// 删除
const handleDelete = (id) => {
    ElMessageBox.confirm('确定要删除该学生吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(async () => {
        try {
            const res = await request.delete(`/students/${id}`)
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            }
        } catch {
            ElMessage.error('删除失败')
        }
    }).catch(() => { })
}

// 初始化
onMounted(() => {
    searchKeyword.value = route.query.keyword || ''
    genderFilter.value = route.query.gender ? route.query.gender.split(',').map(Number) : []
    dateRange.value = route.query.start_date && route.query.end_date ? [route.query.start_date, route.query.end_date] : []
    currentPage.value = Number(route.query.page) || 1
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
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    background: #fff;
    padding: 12px 16px;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.gender-group {
    margin-right: 4px;
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