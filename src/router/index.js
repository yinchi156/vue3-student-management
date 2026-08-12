import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import StudentsView from '../views/StudentsView.vue'
import ClassesView from '../views/ClassesView.vue'
import SubjectsView from '../views/SubjectsView.vue'
import UsersView from '../views/UsersView.vue'
import StatisticsView from '../views/StatisticsView.vue'
import TeacherLayout from '../views/teacher/TeacherLayout.vue'
import MyClasses from '../views/teacher/MyClasses.vue'
import ScoreEntry from '../views/teacher/ScoreEntry.vue'
import ScoreView from '../views/teacher/ScoreView.vue'
import StudentView from '../views/student/StudentView.vue'

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
    {
    path: '/admin',
    component: AdminView,
    meta: { roles: ['admin'] },
    children: [
        {
            // 学生管理（父级，不直接对应组件）
            path: 'students',
            redirect: '/admin/students/list',
            children: [
                { path: 'list', component: StudentsView },
                { path: 'statistics', component: StatisticsView }
            ]
        },
        { path: 'classes', component: ClassesView },
        { path: 'subjects', component: SubjectsView },
        { path: 'users', component: UsersView },
        { path: '', redirect: '/admin/students/list' }
    ]
},

    {
  path: '/teacher',
  component: TeacherLayout,
  meta: { roles: ['admin','teacher'] },
  children: [
    { path: '', redirect: '/teacher/classes' },
    { path: 'classes', component: MyClasses },
    { path: 'score-entry', component: ScoreEntry },
    { path: 'score-view', component: ScoreView }
  ]
},
{
  path: '/student',
  component: StudentView,  // 学生布局（复用 TeacherLayout 的样式，或者新建一个）
  meta: { roles: ['admin','teacher','user'] },
  children: [
    { path: '', redirect: '/student/scores' },
    { path: 'scores', component: StudentView }
  ]
},


  ]
})

router.beforeEach((to) => {
  const role = localStorage.getItem('role') || 'user'
  const allowedRoles = to.meta.roles || []

  // 如果路由没有定义 roles，默认所有人都能访问
  if (allowedRoles.length === 0) {
    return true
  }

  // 检查当前角色是否在允许列表中
  if (allowedRoles.includes(role)) {
    return true
  } else {
    // 无权限，跳转到对应角色的默认页面
    const redirectMap = {
      admin: '/admin/students',
      teacher: '/teacher/classes',
      student: '/student/dashboard'
    }
    return redirectMap[role] || '/login'
  }
})

export default router