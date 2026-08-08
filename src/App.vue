
<template>
  <router-view />
</template>
<style>
/* 这个样式不加 scoped，让它成为全局样式 */
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}
:root {
  --el-color-primary: #409eff;
  --el-color-primary-light-3: #334155;
  --el-color-primary-light-5: #4a5a6e;   /* 输入框聚焦边框颜色 */
  --el-color-primary-light-7: #5a6b7f;   /* 输入框聚焦阴影颜色 */
  --el-color-primary-light-8: #6a7b8f;
  --el-color-primary-light-9: #7a8b9f;
}

</style>