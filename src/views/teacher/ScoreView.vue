<template>
    <div>
        <div class="page-title">📊 成绩查看</div>
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
                <el-button type="primary" @click="queryScores">查询</el-button>
            </div>

            <!-- 成绩列表 -->
            <div v-if="scores.length === 0" class="empty-tip">
                请选择班级和科目，点击「查询」
            </div>
            <el-table v-else :data="scores" border stripe>
                <el-table-column prop="name" label="姓名" />
                <el-table-column label="性别" width="80">
                    <template #default="{ row }">
                        {{ row.gender === 1 ? '男' : '女' }}
                    </template>
                </el-table-column>
                <el-table-column prop="score" label="分数" width="100">
                    <template #default="{ row }">
                        {{ row.score || '未录入' }}
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <!-- 统计信息 -->
        <div v-if="statsVisible"
            style="margin-top: 20px; background: #f8fafc; padding: 16px; border-radius: 8px; display: flex; flex-wrap: wrap; gap: 20px;">
            <div><strong>平均分：</strong>{{ stats.avg || '-' }}</div>
            <div><strong>最高分：</strong>{{ stats.max || '-' }}</div>
            <div><strong>最低分：</strong>{{ stats.min || '-' }}</div>
            <div>
                <strong>及格人数：</strong>{{ stats.pass_count || 0 }} / {{ stats.total || 0 }}
            </div>
            <div><strong>及格率：</strong>{{ stats.pass_rate || 0 }}%</div>
            <div><strong>优秀人数：</strong>{{ stats.excellent_count || 0 }}</div>
            <div><strong>优秀率：</strong>{{ stats.excellent_rate || 0 }}%</div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const classList = ref([])
const subjectList = ref([])
const selectedClass = ref('')
const selectedSubject = ref('')
const scores = ref([])
const stats = ref({})
const statsVisible = ref(false)

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

// 查询成绩
const queryScores = async () => {
    if (!selectedClass.value) {
        ElMessage.warning('请先选择班级')
        return
    }
    if (!selectedSubject.value) {
        ElMessage.warning('请先选择科目')
        return
    }

    try {
        const res = await request.get('/scores/by-class-subject', {
            params: {
                class_id: selectedClass.value,
                subject_id: selectedSubject.value
            }
        })
        if (res.data.code === 200) {
            scores.value = res.data.data || []
            stats.value = res.data.stats || {}
            statsVisible.value = true
        } else {
            scores.value = []
            statsVisible.value = false
        }
    } catch {
        ElMessage.error('查询失败')
    }
}

onMounted(() => {
    loadClassList()
    loadSubjectList()
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