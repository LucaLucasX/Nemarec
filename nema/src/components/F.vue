<script>

</script>

<template>

<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>线虫专家系统</title>
</head>
<body>
<div class="background"></div>
<div class="gradient"></div>

<button class="button button-left" @click="$router.push({ name: 'Chat' })">聊天查询</button>
<button class="button button-right" @click="$router.push({ name: 'HelloWorld' })">图片识别</button>

</body>
</html>
</template>

<style>
 /* 设置整个页面的背景颜色 */
  body, html {
    margin: 0;
    padding: 0;
    height: 100%;
  }

.background::before {
  content: '线虫专家系统';
  position: absolute;
  top: 45%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 60px; /* 根据需要调整字体大小 */
  color: white; /* 设置文字颜色 */
  font-weight: bolder; /* 设置字体粗细 */
  z-index: 1; /* 确保文字显示在背景之上 */
  text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.5), -4px -4px 8px rgba(255, 255, 255, 0.3);
  transition: transform 0.5s ease; /* 增加过渡持续时间 */
}

/* 当鼠标悬停在字体上时，放大字体 */

  /* 渐变效果 */
  .gradient {
    position: absolute;
    width: 100%;
    height: 25%; /* 空白部分占据四分之一 */
    bottom: 0;
    background: linear-gradient(to top, white, transparent); /* 从下到上的渐变 */
  }
/* 设置背景图片和渐变效果 */
/* 设置背景渐变效果，由上到下逐渐变浅，并结合背景图片 */
  .background {
    position: fixed;
    width: 100%;
    height: 75%; /* 图片占据四分之三 */
    background-image: linear-gradient(to bottom, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.45)), url('../assets/background.jpg'); /* 创建渐变和添加背景图片 */
    background-size: cover;
    background-position: center;
  }
  .background::before {
    letter-spacing: 0.35em; /* 增加字体间距，相对于当前字体大小 */
  }
/* 按钮样式 */
.button {
  position: absolute;
  width: 150px;
  height: 125px;
  bottom: 85px; /* 根据需要调整距离底部的距离 */
  background-color: white;
  border: none;
  border-radius: 10px; /* 使得按钮稍微有点圆角 */
  cursor: pointer;
  text-align: center;
  line-height: 100px; /* 使得文字垂直居中 */
  font-size: 20px;
  font-weight: bold; /* 设置字体粗细 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* x偏移量, y偏移量, 模糊半径, 颜色 */
  transition: all 0.5s ease; /* 增加过渡持续时间 */
}
  .button:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  }


  /* 调整两个按钮的位置 */
  .button-left {
    left: 200px; /* 根据需要调整距离左侧的距离 */
  }

  .button-right {
    right: 200px; /* 根据需要调整距离右侧的距离 */
  }
</style>