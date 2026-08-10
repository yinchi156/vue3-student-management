<template>
    <el-container style="height: 100vh;overflow: hidden;">
        <!-- 顶栏 -->
        <el-header
            style="background: #fff; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;">
            <span style="font-size: 18px; font-weight: bold;">学生管理系统</span>
            <el-dropdown trigger="click" @command="handleCommand">
                <div style="display: flex; align-items: center; cursor: pointer; gap: 8px;">
                    <el-avatar :size="36" style="background-color: #409eff;">
                        {{ username.charAt(0).toUpperCase() }}
                    </el-avatar>
                    <span>{{ username }}</span>
                </div>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item disabled>{{ username }}</el-dropdown-item>
                        <el-dropdown-item divided command="profile">个人设置</el-dropdown-item>
                        <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </el-header>

        <!-- 主体 -->
        <el-container>
            <!-- 侧边栏 -->
            <el-aside width="200px" style="background-color: #1e293b;">
                <el-menu :default-active="$route.path" router background-color="#1e293b" text-color="#fff"
                    active-text-color="#409eff">
                    <el-menu-item index="/admin/students">
                        <el-icon>
                            <DataBoard />
                        </el-icon>
                        <span>学生管理</span>
                    </el-menu-item>
                    <el-menu-item index="/admin/classes">
                        <el-icon>
                            <User />
                        </el-icon>
                        <span>班级管理</span>
                    </el-menu-item>
                    <el-menu-item index="/admin/projects">
                        <el-icon>
                            <UserFilled />
                        </el-icon>
                        <span>科目管理</span>
                    </el-menu-item>
                    <el-menu-item index="/admin/admins">
                        <el-icon>
                            <Setting />
                        </el-icon>
                        <span>管理员管理</span>
                    </el-menu-item>
                </el-menu>
            </el-aside>

            <!-- 主内容区 -->
            <el-main style="background: #f5f7fa; padding: 20px;">
                <router-view />
            </el-main>
        </el-container>
    </el-container>

</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataBoard, User, UserFilled, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const username = ref(localStorage.getItem('loggedInUser') || '管理员')

const handleCommand = (command) => {
    if (command === 'logout') {
        localStorage.clear()
        ElMessage.success('已退出')
        router.push('/login')
    }
}
</script>

<style scoped></style>