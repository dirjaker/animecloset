<template>
  <canvas
    ref="canvasRef"
    :width="width"
    :height="height"
    :style="{ width: width + 'px', height: height + 'px' }"
  />
</template>

<script setup>
/**
 * AvatarCanvas - 纸娃娃 (Paper Doll) 画布组件
 * 使用 Canvas 2D API 绘制简单可爱的动漫风格角色
 * 支持分层渲染：身体、头发、眼睛、服装
 */
import { ref, watch, onMounted, computed } from 'vue'
import { SKIN_COLORS, HAIR_COLORS, EYE_COLORS, getGarmentColor } from '../utils/colorMap.js'

const props = defineProps({
  width: { type: Number, default: 200 },
  height: { type: Number, default: 300 },
  avatarConfig: {
    type: Object,
    default: () => ({ hair_id: 1, skin_id: 1, eye_id: 'brown', body_id: 'medium' }),
  },
  garments: {
    type: Array,
    default: () => [],
  },
})

const canvasRef = ref(null)

// 获取颜色
const skinColor = computed(() => SKIN_COLORS[props.avatarConfig?.skin_id] || SKIN_COLORS[1])
const hairColor = computed(() => HAIR_COLORS[props.avatarConfig?.hair_id] || HAIR_COLORS[1])
const eyeColor = computed(() => EYE_COLORS[props.avatarConfig?.eye_id] || EYE_COLORS.brown)

/**
 * 按服装类别分类
 */
const categorizedGarments = computed(() => {
  const result = {}
  for (const g of props.garments) {
    const cat = g.category || '上衣'
    result[cat] = g
  }
  return result
})

/**
 * 绘制角色
 */
function drawAvatar() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const w = props.width
  const h = props.height

  // 清空画布
  ctx.clearRect(0, 0, w, h)

  // 绘制比例参数（基于画布尺寸自动缩放）
  const scale = Math.min(w / 200, h / 300)
  ctx.save()
  ctx.translate(w / 2, h * 0.48) // 以脖子处为锚点
  ctx.scale(scale, scale)

  // 1. 绘制下装（腿部后面的）
  drawLowerBody(ctx)

  // 2. 绘制鞋子
  drawShoes(ctx)

  // 3. 绘制身体
  drawBody(ctx)

  // 4. 绘制外套（在上衣外面）
  if (categorizedGarments.value['外套']) {
    drawOuter(ctx)
  }

  // 5. 绘制上衣
  drawUpperBody(ctx)

  // 6. 绘制手臂
  drawArms(ctx)

  // 7. 绘制头部
  drawHead(ctx)

  // 8. 绘制头发
  drawHair(ctx)

  // 9. 绘制眼睛
  drawEyes(ctx)

  // 10. 绘制嘴巴
  drawMouth(ctx)

  // 11. 绘制配饰
  if (categorizedGarments.value['配饰']) {
    drawAccessory(ctx)
  }

  // 12. 绘制帽子
  if (categorizedGarments.value['帽子']) {
    drawHat(ctx)
  }

  ctx.restore()
}

/**
 * 绘制头部
 */
function drawHead(ctx) {
  const skin = skinColor.value
  ctx.fillStyle = skin
  ctx.strokeStyle = darken(skin, 30)
  ctx.lineWidth = 1.5

  // 头部 - 椭圆形
  ctx.beginPath()
  ctx.ellipse(0, -45, 32, 35, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()

  // 耳朵
  ctx.beginPath()
  ctx.ellipse(-30, -38, 6, 8, -0.2, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
  ctx.beginPath()
  ctx.ellipse(30, -38, 6, 8, 0.2, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
}

/**
 * 绘制眼睛
 */
function drawEyes(ctx) {
  const eye = eyeColor.value
  // 眼白
  ctx.fillStyle = '#FFFFFF'
  ctx.beginPath()
  ctx.ellipse(-12, -48, 8, 10, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(12, -48, 8, 10, 0, 0, Math.PI * 2)
  ctx.fill()

  // 瞳孔
  ctx.fillStyle = eye
  ctx.beginPath()
  ctx.ellipse(-12, -46, 6, 7, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(12, -46, 6, 7, 0, 0, Math.PI * 2)
  ctx.fill()

  // 高光
  ctx.fillStyle = '#FFFFFF'
  ctx.beginPath()
  ctx.arc(-9, -50, 2.5, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.arc(15, -50, 2.5, 0, Math.PI * 2)
  ctx.fill()

  // 睫毛
  ctx.strokeStyle = '#333333'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.arc(-12, -50, 9, -Math.PI * 0.9, -Math.PI * 0.1)
  ctx.stroke()
  ctx.beginPath()
  ctx.arc(12, -50, 9, -Math.PI * 0.9, -Math.PI * 0.1)
  ctx.stroke()
}

/**
 * 绘制嘴巴
 */
function drawMouth(ctx) {
  ctx.strokeStyle = '#E88B8B'
  ctx.lineWidth = 1.5
  ctx.lineCap = 'round'
  ctx.beginPath()
  ctx.arc(0, -35, 5, 0.1, Math.PI - 0.1)
  ctx.stroke()
}

/**
 * 绘制身体（躯干）
 */
function drawBody(ctx) {
  const skin = skinColor.value
  ctx.fillStyle = skin
  ctx.strokeStyle = darken(skin, 30)
  ctx.lineWidth = 1.5

  // 脖子
  ctx.fillRect(-5, -12, 10, 12)
  ctx.strokeRect(-5, -12, 10, 12)

  // 躯干
  ctx.beginPath()
  ctx.moveTo(-28, 0)
  ctx.quadraticCurveTo(-32, 50, -25, 75)
  ctx.lineTo(25, 75)
  ctx.quadraticCurveTo(32, 50, 28, 0)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
}

/**
 * 绘制手臂
 */
function drawArms(ctx) {
  const skin = skinColor.value
  ctx.fillStyle = skin
  ctx.strokeStyle = darken(skin, 30)
  ctx.lineWidth = 1.5

  // 左臂
  ctx.beginPath()
  ctx.moveTo(-28, 2)
  ctx.quadraticCurveTo(-48, 20, -52, 55)
  ctx.lineTo(-44, 57)
  ctx.quadraticCurveTo(-40, 24, -22, 6)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 左手
  ctx.beginPath()
  ctx.ellipse(-50, 58, 6, 7, 0.2, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()

  // 右臂
  ctx.beginPath()
  ctx.moveTo(28, 2)
  ctx.quadraticCurveTo(48, 20, 52, 55)
  ctx.lineTo(44, 57)
  ctx.quadraticCurveTo(40, 24, 22, 6)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 右手
  ctx.beginPath()
  ctx.ellipse(50, 58, 6, 7, -0.2, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
}

/**
 * 绘制上衣
 */
function drawUpperBody(ctx) {
  const garment = categorizedGarments.value['上衣'] || categorizedGarments.value['连衣裙']
  const color = garment ? getGarmentColor(garment) : '#E8D5F5'
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  ctx.beginPath()
  ctx.moveTo(-26, 0)
  ctx.lineTo(-26, 45)
  ctx.quadraticCurveTo(-26, 50, -22, 50)
  ctx.lineTo(22, 50)
  ctx.quadraticCurveTo(26, 50, 26, 45)
  ctx.lineTo(26, 0)
  // 领口
  ctx.lineTo(10, 0)
  ctx.quadraticCurveTo(0, 10, -10, 0)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 袖子（左）
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.moveTo(-26, 0)
  ctx.lineTo(-28, 2)
  ctx.quadraticCurveTo(-48, 20, -52, 55)
  ctx.lineTo(-44, 57)
  ctx.quadraticCurveTo(-40, 24, -22, 6)
  ctx.lineTo(-26, 0)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 袖子（右）
  ctx.beginPath()
  ctx.moveTo(26, 0)
  ctx.lineTo(28, 2)
  ctx.quadraticCurveTo(48, 20, 52, 55)
  ctx.lineTo(44, 57)
  ctx.quadraticCurveTo(40, 24, 22, 6)
  ctx.lineTo(26, 0)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
}

/**
 * 绘制下装（裤子/裙子）
 */
function drawLowerBody(ctx) {
  const garment = categorizedGarments.value['下装']
  const color = garment ? getGarmentColor(garment) : '#A5B4FC'
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  // 裙子或裤子
  if (garment && garment.tags?.style === 'skirt') {
    // 裙子
    ctx.beginPath()
    ctx.moveTo(-25, 50)
    ctx.quadraticCurveTo(-35, 90, -30, 110)
    ctx.lineTo(30, 110)
    ctx.quadraticCurveTo(35, 90, 25, 50)
    ctx.closePath()
    ctx.fill()
    ctx.stroke()
  } else {
    // 裤子（默认）
    // 左腿
    ctx.beginPath()
    ctx.moveTo(-25, 50)
    ctx.lineTo(-25, 120)
    ctx.lineTo(-8, 120)
    ctx.lineTo(-5, 50)
    ctx.closePath()
    ctx.fill()
    ctx.stroke()
    // 右腿
    ctx.beginPath()
    ctx.moveTo(5, 50)
    ctx.lineTo(8, 120)
    ctx.lineTo(25, 120)
    ctx.lineTo(25, 50)
    ctx.closePath()
    ctx.fill()
    ctx.stroke()
  }
}

/**
 * 绘制外套
 */
function drawOuter(ctx) {
  const garment = categorizedGarments.value['外套']
  const color = getGarmentColor(garment)
  ctx.fillStyle = color + '88' // 半透明
  ctx.strokeStyle = darken(color, 20)
  ctx.lineWidth = 2

  ctx.beginPath()
  ctx.moveTo(-32, -2)
  ctx.lineTo(-34, 55)
  ctx.quadraticCurveTo(-34, 60, -30, 60)
  ctx.lineTo(30, 60)
  ctx.quadraticCurveTo(34, 60, 34, 55)
  ctx.lineTo(32, -2)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 袖子覆盖
  ctx.beginPath()
  ctx.moveTo(-32, -2)
  ctx.quadraticCurveTo(-56, 18, -58, 55)
  ctx.lineTo(-50, 57)
  ctx.quadraticCurveTo(-48, 22, -32, 4)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(32, -2)
  ctx.quadraticCurveTo(56, 18, 58, 55)
  ctx.lineTo(50, 57)
  ctx.quadraticCurveTo(48, 22, 32, 4)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
}

/**
 * 绘制鞋子
 */
function drawShoes(ctx) {
  const garment = categorizedGarments.value['鞋子']
  const color = garment ? getGarmentColor(garment) : '#F472B6'
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  // 左鞋
  ctx.beginPath()
  ctx.ellipse(-17, 126, 12, 7, -0.1, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()

  // 右鞋
  ctx.beginPath()
  ctx.ellipse(17, 126, 12, 7, 0.1, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
}

/**
 * 绘制配饰
 */
function drawAccessory(ctx) {
  const garment = categorizedGarments.value['配饰']
  const color = getGarmentColor(garment)

  // 项链
  ctx.strokeStyle = color
  ctx.lineWidth = 2.5
  ctx.beginPath()
  ctx.arc(0, -12, 14, Math.PI * 0.15, Math.PI * 0.85)
  ctx.stroke()

  // 吊坠
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.arc(0, 2, 4, 0, Math.PI * 2)
  ctx.fill()
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1
  ctx.stroke()
}

/**
 * 绘制帽子
 */
function drawHat(ctx) {
  const garment = categorizedGarments.value['帽子']
  const color = getGarmentColor(garment)
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  // 帽檐
  ctx.beginPath()
  ctx.ellipse(0, -72, 42, 8, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()

  // 帽身
  ctx.beginPath()
  ctx.moveTo(-30, -72)
  ctx.quadraticCurveTo(-32, -100, 0, -105)
  ctx.quadraticCurveTo(32, -100, 30, -72)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
}

/**
 * 绘制头发
 */
function drawHair(ctx) {
  const color = hairColor.value
  const hairId = props.avatarConfig?.hair_id || 1
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  switch (hairId) {
    case 1: drawHairShort(ctx, color); break
    case 2: drawHairLong(ctx, color); break
    case 3: drawHairBlonde(ctx, color); break
    case 4: drawHairRed(ctx, color); break
    case 5: drawHairPurple(ctx, color); break
    default: drawHairShort(ctx, color)
  }
}

/**
 * 短发
 */
function drawHairShort(ctx, color) {
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  // 刘海
  ctx.beginPath()
  ctx.moveTo(-30, -50)
  ctx.quadraticCurveTo(-32, -80, -10, -82)
  ctx.quadraticCurveTo(0, -75, 10, -82)
  ctx.quadraticCurveTo(32, -80, 30, -50)
  ctx.quadraticCurveTo(20, -58, 15, -55)
  ctx.quadraticCurveTo(0, -65, -15, -55)
  ctx.quadraticCurveTo(-20, -58, -30, -50)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 头顶
  ctx.beginPath()
  ctx.ellipse(0, -52, 35, 30, 0, Math.PI, 0)
  ctx.fill()
  ctx.stroke()

  // 侧面
  ctx.beginPath()
  ctx.moveTo(-33, -50)
  ctx.quadraticCurveTo(-36, -30, -30, -20)
  ctx.lineTo(-28, -38)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(33, -50)
  ctx.quadraticCurveTo(36, -30, 30, -20)
  ctx.lineTo(28, -38)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
}

/**
 * 长发
 */
function drawHairLong(ctx, color) {
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  // 刘海（遮住额头）
  ctx.beginPath()
  ctx.moveTo(-33, -48)
  ctx.quadraticCurveTo(-35, -82, 0, -85)
  ctx.quadraticCurveTo(35, -82, 33, -48)
  ctx.lineTo(28, -48)
  ctx.quadraticCurveTo(25, -55, 10, -58)
  ctx.quadraticCurveTo(0, -68, -10, -58)
  ctx.quadraticCurveTo(-25, -55, -28, -48)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 头顶
  ctx.beginPath()
  ctx.ellipse(0, -52, 36, 32, 0, Math.PI, 0)
  ctx.fill()
  ctx.stroke()

  // 左侧长发
  ctx.beginPath()
  ctx.moveTo(-33, -48)
  ctx.quadraticCurveTo(-38, -20, -35, 40)
  ctx.quadraticCurveTo(-32, 50, -25, 48)
  ctx.quadraticCurveTo(-30, 20, -28, -10)
  ctx.quadraticCurveTo(-30, -35, -28, -48)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 右侧长发
  ctx.beginPath()
  ctx.moveTo(33, -48)
  ctx.quadraticCurveTo(38, -20, 35, 40)
  ctx.quadraticCurveTo(32, 50, 25, 48)
  ctx.quadraticCurveTo(30, 20, 28, -10)
  ctx.quadraticCurveTo(30, -35, 28, -48)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
}

/**
 * 金色头发（波浪短发）
 */
function drawHairBlonde(ctx, color) {
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  // 蓬松的波浪短发
  ctx.beginPath()
  ctx.moveTo(-36, -45)
  ctx.quadraticCurveTo(-38, -85, 0, -88)
  ctx.quadraticCurveTo(38, -85, 36, -45)
  // 波浪边缘
  ctx.quadraticCurveTo(34, -30, 30, -20)
  ctx.quadraticCurveTo(26, -28, 22, -35)
  ctx.quadraticCurveTo(15, -25, 10, -38)
  ctx.quadraticCurveTo(5, -28, 0, -40)
  ctx.quadraticCurveTo(-5, -28, -10, -38)
  ctx.quadraticCurveTo(-15, -25, -22, -35)
  ctx.quadraticCurveTo(-26, -28, -30, -20)
  ctx.quadraticCurveTo(-34, -30, -36, -45)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 头顶
  ctx.beginPath()
  ctx.ellipse(0, -55, 38, 34, 0, Math.PI, 0)
  ctx.fill()
  ctx.stroke()
}

/**
 * 红发（双马尾）
 */
function drawHairRed(ctx, color) {
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  // 刘海
  ctx.beginPath()
  ctx.moveTo(-30, -48)
  ctx.quadraticCurveTo(-32, -80, 0, -84)
  ctx.quadraticCurveTo(32, -80, 30, -48)
  ctx.lineTo(25, -50)
  ctx.quadraticCurveTo(15, -60, 0, -55)
  ctx.quadraticCurveTo(-15, -60, -25, -50)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 头顶
  ctx.beginPath()
  ctx.ellipse(0, -52, 35, 30, 0, Math.PI, 0)
  ctx.fill()
  ctx.stroke()

  // 左马尾
  drawPonytail(ctx, -30, -42, -40, 20, color)
  // 右马尾
  drawPonytail(ctx, 30, -42, 40, 20, color)
}

/**
 * 紫色头发（齐刘海长发）
 */
function drawHairPurple(ctx, color) {
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  // 齐刘海
  ctx.beginPath()
  ctx.moveTo(-33, -48)
  ctx.lineTo(-33, -55)
  ctx.quadraticCurveTo(-35, -82, 0, -85)
  ctx.quadraticCurveTo(35, -82, 33, -55)
  ctx.lineTo(33, -48)
  ctx.lineTo(-33, -48)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 头顶
  ctx.beginPath()
  ctx.ellipse(0, -55, 36, 32, 0, Math.PI, 0)
  ctx.fill()
  ctx.stroke()

  // 左侧长发
  ctx.beginPath()
  ctx.moveTo(-33, -48)
  ctx.quadraticCurveTo(-38, -15, -36, 50)
  ctx.quadraticCurveTo(-33, 58, -26, 55)
  ctx.quadraticCurveTo(-30, 15, -28, -20)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 右侧长发
  ctx.beginPath()
  ctx.moveTo(33, -48)
  ctx.quadraticCurveTo(38, -15, 36, 50)
  ctx.quadraticCurveTo(33, 58, 26, 55)
  ctx.quadraticCurveTo(30, 15, 28, -20)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
}

/**
 * 绘制马尾辫
 */
function drawPonytail(ctx, startX, startY, offsetX, length, color) {
  ctx.fillStyle = color
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.5

  // 发绳
  ctx.beginPath()
  ctx.arc(startX, startY, 5, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()

  // 马尾
  ctx.beginPath()
  ctx.moveTo(startX - 4, startY)
  ctx.quadraticCurveTo(offsetX - 10, startY + length / 2, offsetX - 5, startY + length)
  ctx.quadraticCurveTo(offsetX, startY + length + 10, offsetX + 5, startY + length)
  ctx.quadraticCurveTo(offsetX + 10, startY + length / 2, startX + 4, startY)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
}

/**
 * 颜色加深
 */
function darken(hex, amount) {
  let color = hex.replace('#', '')
  if (color.length === 3) {
    color = color[0] + color[0] + color[1] + color[1] + color[2] + color[2]
  }
  const r = Math.max(0, parseInt(color.substring(0, 2), 16) - amount)
  const g = Math.max(0, parseInt(color.substring(2, 4), 16) - amount)
  const b = Math.max(0, parseInt(color.substring(4, 6), 16) - amount)
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

// 监听 props 变化，重新绘制
watch(
  () => [props.width, props.height, props.avatarConfig, props.garments],
  () => drawAvatar(),
  { deep: true }
)

onMounted(() => drawAvatar())
</script>

<style scoped>
canvas {
  display: block;
}
</style>
