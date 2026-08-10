<template>
    <div class="teacher-layout">
        <!-- 顶栏 -->
        <div class="topbar">
            <div class="logo">📚 教师管理平台</div>
            <div class="user-info">
                <span class="username">👤 {{ username }}</span>
                <el-button size="small" @click="handleLogout">退出登录</el-button>
            </div>
        </div>

        <!-- 主体 -->
        <div class="main-layout">
            <!-- 侧边栏 -->
            <div class="sidebar">
                <div v-for="item in menus" :key="item.path" class="nav-item"
                    :class="{ active: $route.path === item.path }" @click="navigateTo(item.path)">
                    <span class="icon">{{ item.icon }}</span>
                    {{ item.label }}
                </div>
            </div>

            <!-- 内容区 -->
            <div class="content-area">
                <router-view />
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const username = ref(localStorage.getItem('loggedInUser') || '教师')

const menus = [
    { path: '/teacher/classes', label: '我的班级', icon: '📋' },
    { path: '/teacher/score-entry', label: '成绩录入', icon: '✏️' },
    { path: '/teacher/score-view', label: '成绩查看', icon: '📊' }
]

const navigateTo = (path) => {
    router.push(path)
}

const handleLogout = () => {
    localStorage.clear()
    ElMessage.success('已退出')
    router.push('/login')
}
</script>

<style scoped>
.teacher-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #f5f7fa;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
    background: #1e2a3a;
    color: white;
    height: 60px;
    flex-shrink: 0;
}

.logo {
    font-size: 18px;
    font-weight: 600;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 16px;
}

.username {
    background: rgba(255, 255, 255, 0.15);
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 14px;
}

.main-layout {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.sidebar {
    width: 200px;
    background: white;
    border-right: 1px solid #e4e7ed;
    padding: 16px 0;
    flex-shrink: 0;
    overflow-y: auto;
}

.nav-item {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    cursor: pointer;
    font-size: 14px;
    color: #333;
    border-left: 3px solid transparent;
    transition: 0.2s;
}

.nav-item:hover {
    background: #f0f4f8;
}

.nav-item.active {
    background: #eef2f6;
    border-left-color: #1e2a3a;
    font-weight: 500;
}

.nav-item .icon {
    margin-right: 10px;
    font-size: 16px;
}

.content-area {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
}
</style>