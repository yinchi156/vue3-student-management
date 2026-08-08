import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import StudentsView from '../views/StudentsView.vue'

const router = createRouter({
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
    { path: '', redirect: '/admin/students' }  // 默认显示学生管理
    // 先只加一个，测试通过后再加其他的
  ]
  //     children: [
  //   { path: 'students', component: StudentsView },
  //   // { path: 'classes', component: ClassesView },
  //   // { path: 'projects', component: ProjectsView },
  //   // { path: 'admins', component: AdminsView },
  //   { path: '', redirect: 'students' }  // 默认显示仪表盘
  // ]
    },

  ]
})

export default router