import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import StudentsView from '../views/StudentsView.vue'
import ClassesView from '../views/ClassesView.vue'
import SubjectsView from '../views/SubjectsView.vue'
import UsersView from '../views/UsersView.vue'

const router = createRouter({
  // 路由模式：HTML5 历史模式（无 # 号）
  // 路径前缀从 vite.config.js 的 base 配置读取
  // 默认是 '/'，部署到子目录时修改 base 即可
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    { path: '/admin', component: AdminView,
      children: [
    { path: 'students', component: StudentsView },
    { path: 'classes', component: ClassesView },
    { path: 'subjects', component: SubjectsView },
    { path: 'users', component: UsersView },
    { path: '', redirect: '/admin/students' }  // 默认显示学生管理
  ]
    },

  ]
})

export default router