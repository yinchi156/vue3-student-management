<template>
    <div class="login-container">
        <div class="form-card">
            <h2 class="form-title">登录</h2>

            <form @submit.prevent="handleLogin">
                <div class="form-group">
                    <label for="username" class="form-label">用户名/账号</label>
                    <el-input id="username" v-model="loginForm.username" type="text" placeholder="请输入用户名/账号"
                        autocomplete="off" size="large" />
                </div>

                <div class="form-group">
                    <label for="password" class="form-label">密码</label>
                    <el-input id="password" v-model="loginForm.password" type="password" placeholder="请输入密码"
                        autocomplete="off" show-password size="large" />
                </div>

                <!-- 验证码区域 -->
                <div class="form-group captcha-group">
                    <label for="captcha" class="form-label">验证码</label>
                    <el-input v-model="loginForm.captcha" placeholder="请输入验证码" size="large" class="captcha-input">
                        <template #suffix>
                            <img :src="captchaSrc" alt="验证码"
                                style="height: 36px; width: 110px; cursor: pointer; border-radius: 4px;"
                                @click="refreshCaptcha" />
                        </template>
                    </el-input>
                </div>

                <el-button native-type="submit" type="primary" color="#3B82FF" size="large" class="btn-submit"
                    style="width: 100%; margin-top: 0.4rem;">登录</el-button>
                <!-- <div style="text-align: center; margin-top: 15px">
                    <a href="#" class="btn-register" @click.prevent="goToRegister">还没有账号？立即注册</a>
                </div> -->
            </form>
        </div>
    </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
const captchaSrc = ref('')
const captchaKey = ref('')
const router = useRouter()

const loginForm = reactive({
    username: '',
    password: '',
    captcha: ''
})

const fetchCaptcha = async () => {
    try {
        const res = await request.get('/captcha?t=' + Date.now())
        // 注意这里的键名改为 captcha-image 和 captcha-hash
        captchaSrc.value = res.data.image      // 对应 'captcha-image'
        captchaKey.value = res.data.key        // 对应 'captcha-hash'
    } catch {
        console.log('获取验证码失败')
    }
}

const refreshCaptcha = () => {
    fetchCaptcha()
}

onMounted(() => {
    fetchCaptcha()
})

// 后端API地址（这里改成你自己的实际地址）


const handleLogin = async () => {
    const { username, password, } = loginForm

    if (!username || !password) {
        alert('⚠️ 用户名和密码都不能为空！')
        return
    }

    try {
        const response = await request.post('/login', {
            username,
            password,
            captcha: loginForm.captcha.toUpperCase(),      // 用户输入的验证码
            captchaKey: captchaKey.value     // 用于后端匹配
        })

        const { token, role, username: userName } = response.data

        localStorage.setItem('loggedInUser', userName)
        localStorage.setItem('token', token)
        localStorage.setItem('role', role)
        localStorage.setItem('loginTime', Date.now())
        ElMessage.success(`欢迎回来，${userName}`)

        if (role === 'admin') {
            router.push('/admin')
        } else if (role === 'teacher') {
            router.push('/teacher')
        } else {
            router.push('/student')
        }
    } catch (error) {
        const msg = error.response?.data?.message || '登录失败'
        alert('❌ ' + msg)
        // 如果错误信息包含"验证码"，自动刷新验证码
        if (msg.includes('验证码')) {
            fetchCaptcha()        // 刷新验证码
            loginForm.captcha = '' // 清空输入框
        }
    }
}
// const goToRegister = () => {
//     alert('注册功能开发中...')
// }
</script>

<style scoped>
/* 全局重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.login-container {
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;

    /* 1. 基础色：灰白 */
    background-color: #f0f2f5;

    /* 2. 嵌入 SVG 曲线背景（Base64 编码，无需外部文件） */
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25' viewBox='0 0 1200 800'%3E%3Cdefs%3E%3Cpath id='wave' d='M0 600 Q 200 400 400 500 T 800 450 T 1200 550 L 1200 800 L 0 800 Z' fill='rgba(200,210,220,0.3)' /%3E%3Cpath id='wave2' d='M0 650 Q 300 500 600 600 T 1200 500 L 1200 800 L 0 800 Z' fill='rgba(180,190,200,0.2)' /%3E%3C/defs%3E%3Crect width='1200' height='800' fill='%23f0f2f5' /%3E%3Cuse href='%23wave' /%3E%3Cuse href='%23wave2' /%3E%3C/svg%3E");
    background-size: cover;
    background-position: center;
}

/* 卡片样式：纯白、干净、有质感 */
.form-card {
    background: #ffffff;
    border-radius: 8px;
    box-shadow:
        0 10px 40px rgba(0, 0, 0, 0.06),
        0 4px 12px rgba(0, 0, 0, 0.03);
    padding: 2.8rem 3rem;
    max-width: 440px;
    width: 100%;
    border: 1px solid rgba(255, 255, 255, 0.8);
    transition: box-shadow 0.2s ease;
}

/* 其他样式保持不变（你的表单元素样式已经很好了） */
.form-title {
    font-size: 1.5rem;
    font-weight: 500;
    color: #1e293b;
    margin-bottom: 1.8rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid #eef2f6;
    letter-spacing: -0.01em;
}

.form-group {
    margin-bottom: 1.6rem;
}

.form-label {
    display: block;
    font-size: 0.9rem;
    font-weight: 500;
    color: #334155;
    margin-bottom: 0.4rem;
}

.form-input {
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-family: inherit;
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    color: #0f172a;
}

.form-input:focus {
    border-color: #94a3b8;
    box-shadow: 0 0 0 4px rgba(148, 163, 184, 0.1);
}

.form-input::placeholder {
    color: #94a3b8;
    font-weight: 400;
}

.captcha-group {
    margin-top: 2rem;
    /* 与上面输入框拉开距离 */
}

.captcha-wrapper {
    display: flex;
    align-items: center;
    gap: 16px;
}

.captcha-input {
    flex: 1;
}

.captcha-image {
    flex-shrink: 0;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.captcha-image img {
    height: 48px;
    border-radius: 8px;
    border: 1px solid #dce1e9;
}

.refresh-tip {
    font-size: 12px;
    color: #94a3b8;
}

.btn-submit {
    font-size: 16px;
    letter-spacing: 0.3px;
}

.btn-submit:active {
    transform: scale(0.97);
}

.btn-register {
    display: inline-block;
    color: #475569;
    text-decoration: none;
    font-size: 0.9rem;
    padding: 8px 20px;
    border: 1.5px solid #e2e8f0;
    border-radius: 30px;
    transition: all 0.2s;
}

.btn-register:hover {
    background: #1e293b;
    color: white;
    border-color: #1e293b;
}

.captcha-input :deep(.el-input__suffix) {
    padding-right: 0;
    margin-right: -13px;
}

@media (max-width: 480px) {
    .form-card {
        padding: 2rem 1.5rem;
    }

    .form-title {
        font-size: 1.3rem;
    }
}
</style>