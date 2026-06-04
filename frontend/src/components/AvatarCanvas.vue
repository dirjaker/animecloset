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
 * 使用 Canvas 2D API 绘制精细 Q 版动漫风格角色
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

  // 0. 绘制地面阴影
  drawGroundShadow(ctx)

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

  // 8. 绘制腮红
  drawBlush(ctx)

  // 9. 绘制头发
  drawHair(ctx)

  // 10. 绘制眼睛
  drawEyes(ctx)

  // 11. 绘制嘴巴
  drawMouth(ctx)

  // 12. 绘制配饰
  if (categorizedGarments.value['配饰']) {
    drawAccessory(ctx)
  }

  // 13. 绘制帽子
  if (categorizedGarments.value['帽子']) {
    drawHat(ctx)
  }

  ctx.restore()
}

/**
 * 绘制地面阴影（淡淡的椭圆）
 */
function drawGroundShadow(ctx) {
  ctx.save()
  ctx.fillStyle = 'rgba(0, 0, 0, 0.08)'
  ctx.beginPath()
  ctx.ellipse(0, 132, 45, 8, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.restore()
}

/**
 * 绘制头部 — Q 版风格：圆润的大头，头身比约 1:2.5
 */
function drawHead(ctx) {
  const skin = skinColor.value
  const outlineColor = darken(skin, 35)

  ctx.save()

  // 头部主体 — 更圆润的形状（接近圆形，下巴微微收窄）
  ctx.fillStyle = skin
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  ctx.beginPath()
  // 用贝塞尔曲线画一个圆润的 Q 版头部
  ctx.moveTo(0, -82) // 头顶
  ctx.bezierCurveTo(36, -82, 40, -55, 36, -40) // 右上到右中
  ctx.bezierCurveTo(34, -25, 24, -10, 0, -8) // 右下到下巴
  ctx.bezierCurveTo(-24, -10, -34, -25, -36, -40) // 左下到左中
  ctx.bezierCurveTo(-40, -55, -36, -82, 0, -82) // 左上到头顶
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 耳朵 — 更立体
  // 左耳
  ctx.fillStyle = skin
  ctx.beginPath()
  ctx.ellipse(-34, -44, 6, 9, -0.15, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
  // 左耳内侧
  ctx.fillStyle = darken(skin, 18)
  ctx.beginPath()
  ctx.ellipse(-34, -44, 3.5, 5.5, -0.15, 0, Math.PI * 2)
  ctx.fill()

  // 右耳
  ctx.fillStyle = skin
  ctx.beginPath()
  ctx.ellipse(34, -44, 6, 9, 0.15, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
  // 右耳内侧
  ctx.fillStyle = darken(skin, 18)
  ctx.beginPath()
  ctx.ellipse(34, -44, 3.5, 5.5, 0.15, 0, Math.PI * 2)
  ctx.fill()

  ctx.restore()
}

/**
 * 绘制腮红 — 粉色椭圆在脸颊两侧
 */
function drawBlush(ctx) {
  ctx.save()
  ctx.fillStyle = 'rgba(255, 150, 150, 0.3)'
  ctx.beginPath()
  ctx.ellipse(-22, -36, 10, 6, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(22, -36, 10, 6, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.restore()
}

/**
 * 绘制眼睛 — 大动漫眼睛：多层渐变、大高光、精致睫毛
 */
function drawEyes(ctx) {
  const eye = eyeColor.value
  ctx.save()

  // 眼睛参数
  const eyeW = 10
  const eyeH = 12
  const eyeY = -52
  const leftX = -14
  const rightX = 14

  // === 左眼 ===
  _drawAnimeEye(ctx, leftX, eyeY, eyeW, eyeH, eye, false)
  // === 右眼 ===
  _drawAnimeEye(ctx, rightX, eyeY, eyeW, eyeH, eye, true)

  ctx.restore()
}

/**
 * 绘制单个动漫风格大眼睛
 */
function _drawAnimeEye(ctx, cx, cy, w, h, irisColor, isRight) {
  ctx.save()

  // 眼白
  ctx.fillStyle = '#FFFFFF'
  ctx.strokeStyle = darken(irisColor, 50)
  ctx.lineWidth = 1.2
  ctx.beginPath()
  ctx.ellipse(cx, cy, w + 1, h, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()

  // 虹膜 — 多层渐变
  const grad = ctx.createRadialGradient(cx, cy - 2, 0, cx, cy, h - 1)
  grad.addColorStop(0, lighten(irisColor, 40))
  grad.addColorStop(0.4, irisColor)
  grad.addColorStop(0.85, darken(irisColor, 30))
  grad.addColorStop(1, darken(irisColor, 50))
  ctx.fillStyle = grad
  ctx.beginPath()
  ctx.ellipse(cx, cy + 1, w - 1, h - 1, 0, 0, Math.PI * 2)
  ctx.fill()

  // 瞳孔深色区域（底部）
  ctx.fillStyle = darken(irisColor, 60)
  ctx.beginPath()
  ctx.ellipse(cx, cy + 3, w - 3, h - 4, 0, 0, Math.PI * 2)
  ctx.globalAlpha = 0.3
  ctx.fill()
  ctx.globalAlpha = 1

  // 大高光（上左/右）
  const hlX = isRight ? cx + 3 : cx - 3
  ctx.fillStyle = '#FFFFFF'
  ctx.beginPath()
  ctx.ellipse(hlX, cy - 3, 3.5, 4, isRight ? -0.2 : 0.2, 0, Math.PI * 2)
  ctx.fill()

  // 小高光（下右/左）
  const hl2X = isRight ? cx - 2.5 : cx + 2.5
  ctx.fillStyle = 'rgba(255, 255, 255, 0.7)'
  ctx.beginPath()
  ctx.arc(hl2X, cy + 3, 2, 0, Math.PI * 2)
  ctx.fill()

  // 上眼睑线 — 粗且有弧度
  ctx.strokeStyle = '#3a2a2a'
  ctx.lineWidth = 2.8
  ctx.lineCap = 'round'
  ctx.beginPath()
  ctx.ellipse(cx, cy, w + 1, h, 0, Math.PI + 0.3, -0.3)
  ctx.stroke()

  // 上睫毛 — 3 根精致睫毛
  ctx.strokeStyle = '#3a2a2a'
  ctx.lineWidth = 1.8
  ctx.lineCap = 'round'
  const lashSide = isRight ? 1 : -1
  for (let i = 0; i < 3; i++) {
    const angle = isRight ? (-Math.PI * 0.7 + i * 0.25) : (-Math.PI * 0.3 + i * 0.25)
    const startX = cx + Math.cos(angle) * (w + 1)
    const startY = cy + Math.sin(angle) * h
    ctx.beginPath()
    ctx.moveTo(startX, startY)
    ctx.lineTo(startX + lashSide * (3 - i * 0.5), startY - (4 + i))
    ctx.stroke()
  }

  // 下眼睑 — 细细的下眼线
  ctx.strokeStyle = 'rgba(100, 70, 70, 0.5)'
  ctx.lineWidth = 1.2
  ctx.beginPath()
  ctx.ellipse(cx, cy, w, h - 1, 0, 0.3, Math.PI - 0.3)
  ctx.stroke()

  // 下睫毛 — 几根细小睫毛
  ctx.strokeStyle = 'rgba(100, 70, 70, 0.4)'
  ctx.lineWidth = 1
  for (let i = 0; i < 3; i++) {
    const angle = Math.PI * 0.5 + (i - 1) * 0.35
    const sx = cx + Math.cos(angle) * (w - 1)
    const sy = cy + Math.sin(angle) * (h - 2)
    ctx.beginPath()
    ctx.moveTo(sx, sy)
    ctx.lineTo(sx + lashSide * 0.5, sy + 3)
    ctx.stroke()
  }

  ctx.restore()
}

/**
 * 绘制嘴巴 — 微笑弧线
 */
function drawMouth(ctx) {
  ctx.save()
  ctx.lineCap = 'round'

  // 小巧微笑嘴巴
  ctx.strokeStyle = '#d4737a'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(-6, -36)
  ctx.quadraticCurveTo(0, -30, 6, -36)
  ctx.stroke()

  // 嘴巴内部微粉色
  ctx.fillStyle = 'rgba(210, 110, 120, 0.3)'
  ctx.beginPath()
  ctx.moveTo(-4, -36)
  ctx.quadraticCurveTo(0, -32, 4, -36)
  ctx.closePath()
  ctx.fill()

  ctx.restore()
}

/**
 * 绘制身体（躯干）— 更自然曲线，肩膀有弧度
 */
function drawBody(ctx) {
  const skin = skinColor.value
  const outlineColor = darken(skin, 35)

  ctx.save()
  ctx.fillStyle = skin
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  // 脖子 — 更自然的梯形
  ctx.beginPath()
  ctx.moveTo(-7, -8)
  ctx.lineTo(-6, 0)
  ctx.lineTo(6, 0)
  ctx.lineTo(7, -8)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 躯干 — Q 版风格，圆润有弧度
  ctx.beginPath()
  ctx.moveTo(-28, 2) // 左肩
  // 左肩弧度
  ctx.quadraticCurveTo(-30, -2, -24, 0)
  ctx.quadraticCurveTo(-20, -2, -7, 0)
  ctx.lineTo(7, 0)
  ctx.quadraticCurveTo(20, -2, 24, 0)
  ctx.quadraticCurveTo(30, -2, 28, 2) // 右肩
  // 右侧身体曲线
  ctx.quadraticCurveTo(30, 30, 26, 50)
  ctx.quadraticCurveTo(24, 58, 18, 62)
  // 底部
  ctx.lineTo(-18, 62)
  ctx.quadraticCurveTo(-24, 58, -26, 50)
  ctx.quadraticCurveTo(-30, 30, -28, 2)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  ctx.restore()
}

/**
 * 绘制手臂 — 圆润，有手掌
 */
function drawArms(ctx) {
  const skin = skinColor.value
  const outlineColor = darken(skin, 35)
  ctx.save()

  _drawArm(ctx, skin, outlineColor, -1)
  _drawArm(ctx, skin, outlineColor, 1)

  ctx.restore()
}

function _drawArm(ctx, skin, outlineColor, side) {
  const s = side // -1 left, 1 right
  ctx.fillStyle = skin
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  // 上臂 + 前臂（一条流畅曲线）
  ctx.beginPath()
  ctx.moveTo(s * 28, 2) // 肩膀起点
  ctx.quadraticCurveTo(s * 40, 15, s * 42, 30) // 上臂
  ctx.quadraticCurveTo(s * 44, 45, s * 46, 55) // 前臂
  // 手掌 — 圆润
  ctx.quadraticCurveTo(s * 50, 62, s * 48, 66)
  ctx.quadraticCurveTo(s * 44, 70, s * 40, 66)
  // 内侧回程
  ctx.quadraticCurveTo(s * 38, 55, s * 36, 40)
  ctx.quadraticCurveTo(s * 34, 25, s * 22, 6)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 手掌细节 — 小圆手指暗示
  ctx.fillStyle = darken(skin, 8)
  ctx.beginPath()
  ctx.ellipse(s * 44, 66, 3, 4, s * 0.3, 0, Math.PI * 2)
  ctx.fill()
}

/**
 * 绘制上衣 — 有褶皱线条、领口细节
 */
function drawUpperBody(ctx) {
  const garment = categorizedGarments.value['上衣'] || categorizedGarments.value['连衣裙']
  const color = garment ? getGarmentColor(garment) : '#E8D5F5'
  const outlineColor = darken(color, 30)

  ctx.save()
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  // 衣身 — 匹配新的躯干曲线
  ctx.beginPath()
  ctx.moveTo(-27, 1)
  ctx.quadraticCurveTo(-29, 30, -25, 50)
  ctx.quadraticCurveTo(-24, 56, -18, 60)
  ctx.lineTo(18, 60)
  ctx.quadraticCurveTo(24, 56, 25, 50)
  ctx.quadraticCurveTo(29, 30, 27, 1)
  // 领口
  ctx.lineTo(12, 1)
  ctx.quadraticCurveTo(6, 12, 0, 10)
  ctx.quadraticCurveTo(-6, 12, -12, 1)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 领口细节 — V 领或圆领
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 1.5
  ctx.beginPath()
  ctx.moveTo(-12, 1)
  ctx.quadraticCurveTo(-4, 14, 0, 12)
  ctx.quadraticCurveTo(4, 14, 12, 1)
  ctx.stroke()

  // 褶皱线条
  ctx.strokeStyle = darken(color, 15)
  ctx.lineWidth = 1
  ctx.globalAlpha = 0.5
  // 左侧褶皱
  ctx.beginPath()
  ctx.moveTo(-15, 15)
  ctx.quadraticCurveTo(-18, 35, -16, 50)
  ctx.stroke()
  // 右侧褶皱
  ctx.beginPath()
  ctx.moveTo(15, 15)
  ctx.quadraticCurveTo(18, 35, 16, 50)
  ctx.stroke()
  // 中间褶皱
  ctx.beginPath()
  ctx.moveTo(0, 14)
  ctx.quadraticCurveTo(-2, 35, 0, 52)
  ctx.stroke()
  ctx.globalAlpha = 1

  // 袖子 — 左
  _drawSleeve(ctx, color, outlineColor, -1)
  // 袖子 — 右
  _drawSleeve(ctx, color, outlineColor, 1)

  ctx.restore()
}

function _drawSleeve(ctx, color, outlineColor, side) {
  const s = side
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  ctx.beginPath()
  ctx.moveTo(s * 27, 1)
  ctx.quadraticCurveTo(s * 30, -1, s * 34, 2)
  ctx.quadraticCurveTo(s * 40, 15, s * 42, 30)
  ctx.quadraticCurveTo(s * 44, 45, s * 46, 55)
  ctx.quadraticCurveTo(s * 50, 62, s * 48, 66)
  ctx.quadraticCurveTo(s * 44, 70, s * 40, 66)
  ctx.quadraticCurveTo(s * 38, 55, s * 36, 40)
  ctx.quadraticCurveTo(s * 34, 25, s * 22, 5)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 袖口细节
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 1.5
  ctx.beginPath()
  ctx.moveTo(s * 48, 66)
  ctx.quadraticCurveTo(s * 44, 62, s * 40, 66)
  ctx.stroke()
}

/**
 * 绘制下装（裤子/裙子）— 有褶皱和细节
 */
function drawLowerBody(ctx) {
  const garment = categorizedGarments.value['下装']
  const color = garment ? getGarmentColor(garment) : '#A5B4FC'
  const outlineColor = darken(color, 30)

  ctx.save()
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  // 裙子或裤子
  if (garment && garment.tags?.style === 'skirt') {
    // 裙子 — 更蓬松的 Q 版风格
    ctx.beginPath()
    ctx.moveTo(-22, 58)
    ctx.quadraticCurveTo(-32, 75, -34, 100)
    ctx.quadraticCurveTo(-35, 108, -30, 112)
    ctx.lineTo(30, 112)
    ctx.quadraticCurveTo(35, 108, 34, 100)
    ctx.quadraticCurveTo(32, 75, 22, 58)
    ctx.closePath()
    ctx.fill()
    ctx.stroke()

    // 裙褶线条
    ctx.strokeStyle = darken(color, 15)
    ctx.lineWidth = 1
    ctx.globalAlpha = 0.4
    for (let i = -2; i <= 2; i++) {
      ctx.beginPath()
      ctx.moveTo(i * 8, 62)
      ctx.quadraticCurveTo(i * 10, 85, i * 11, 108)
      ctx.stroke()
    }
    ctx.globalAlpha = 1
  } else {
    // 裤子 — 更圆润的 Q 版裤型
    // 左腿
    ctx.beginPath()
    ctx.moveTo(-22, 60)
    ctx.quadraticCurveTo(-26, 80, -24, 100)
    ctx.quadraticCurveTo(-23, 115, -20, 122)
    ctx.lineTo(-4, 122)
    ctx.quadraticCurveTo(-6, 115, -5, 100)
    ctx.quadraticCurveTo(-4, 80, -4, 60)
    ctx.closePath()
    ctx.fill()
    ctx.stroke()

    // 右腿
    ctx.beginPath()
    ctx.moveTo(4, 60)
    ctx.quadraticCurveTo(4, 80, 5, 100)
    ctx.quadraticCurveTo(6, 115, 4, 122)
    ctx.lineTo(20, 122)
    ctx.quadraticCurveTo(23, 115, 24, 100)
    ctx.quadraticCurveTo(26, 80, 22, 60)
    ctx.closePath()
    ctx.fill()
    ctx.stroke()

    // 裤缝线条
    ctx.strokeStyle = darken(color, 15)
    ctx.lineWidth = 1
    ctx.globalAlpha = 0.4
    ctx.beginPath()
    ctx.moveTo(-14, 62)
    ctx.quadraticCurveTo(-15, 90, -14, 118)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(14, 62)
    ctx.quadraticCurveTo(15, 90, 14, 118)
    ctx.stroke()
    ctx.globalAlpha = 1
  }

  ctx.restore()
}

/**
 * 绘制外套 — 半透明，有细节
 */
function drawOuter(ctx) {
  const garment = categorizedGarments.value['外套']
  const color = getGarmentColor(garment)
  const outlineColor = darken(color, 20)

  ctx.save()

  // 外套主体 — 半透明
  ctx.globalAlpha = 0.75
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  ctx.beginPath()
  ctx.moveTo(-32, -1)
  ctx.quadraticCurveTo(-34, 30, -30, 55)
  ctx.quadraticCurveTo(-28, 62, -22, 65)
  ctx.lineTo(22, 65)
  ctx.quadraticCurveTo(28, 62, 30, 55)
  ctx.quadraticCurveTo(34, 30, 32, -1)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 外套前襟线条
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 1.5
  ctx.beginPath()
  ctx.moveTo(0, 5)
  ctx.lineTo(0, 60)
  ctx.stroke()

  // 袖子覆盖 — 左
  ctx.beginPath()
  ctx.moveTo(-32, -1)
  ctx.quadraticCurveTo(-36, 2, -42, 15)
  ctx.quadraticCurveTo(-50, 35, -52, 55)
  ctx.quadraticCurveTo(-54, 62, -50, 68)
  ctx.quadraticCurveTo(-46, 72, -42, 68)
  ctx.quadraticCurveTo(-44, 55, -40, 40)
  ctx.quadraticCurveTo(-36, 25, -26, 5)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 袖子覆盖 — 右
  ctx.beginPath()
  ctx.moveTo(32, -1)
  ctx.quadraticCurveTo(36, 2, 42, 15)
  ctx.quadraticCurveTo(50, 35, 52, 55)
  ctx.quadraticCurveTo(54, 62, 50, 68)
  ctx.quadraticCurveTo(46, 72, 42, 68)
  ctx.quadraticCurveTo(44, 55, 40, 40)
  ctx.quadraticCurveTo(36, 25, 26, 5)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  ctx.globalAlpha = 1
  ctx.restore()
}

/**
 * 绘制鞋子 — 更精致，有脚掌形状
 */
function drawShoes(ctx) {
  const garment = categorizedGarments.value['鞋子']
  const color = garment ? getGarmentColor(garment) : '#F472B6'
  const outlineColor = darken(color, 35)

  ctx.save()

  _drawShoe(ctx, color, outlineColor, -1)
  _drawShoe(ctx, color, outlineColor, 1)

  ctx.restore()
}

function _drawShoe(ctx, color, outlineColor, side) {
  const s = side
  const cx = s * 14
  const cy = 126

  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  // 鞋身 — 圆润的 Q 版鞋子
  ctx.beginPath()
  ctx.moveTo(cx - 8, cy - 4)
  ctx.quadraticCurveTo(cx - 12, cy, cx - 10, cy + 5)
  ctx.quadraticCurveTo(cx - 8, cy + 9, cx, cy + 10)
  ctx.quadraticCurveTo(cx + 8, cy + 9, cx + 12, cy + 5)
  ctx.quadraticCurveTo(cx + 14, cy, cx + 10, cy - 4)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 鞋底高光
  ctx.fillStyle = darken(color, 15)
  ctx.beginPath()
  ctx.moveTo(cx - 8, cy + 4)
  ctx.quadraticCurveTo(cx, cy + 8, cx + 10, cy + 4)
  ctx.quadraticCurveTo(cx + 8, cy + 7, cx, cy + 8)
  ctx.quadraticCurveTo(cx - 6, cy + 7, cx - 8, cy + 4)
  ctx.closePath()
  ctx.fill()

  // 鞋面装饰线
  ctx.strokeStyle = darken(color, 20)
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(cx - 4, cy - 2)
  ctx.quadraticCurveTo(cx, cy + 1, cx + 5, cy - 2)
  ctx.stroke()
}

/**
 * 绘制配饰 — 项链+吊坠，更精致
 */
function drawAccessory(ctx) {
  const garment = categorizedGarments.value['配饰']
  const color = getGarmentColor(garment)

  ctx.save()

  // 项链链子
  ctx.strokeStyle = color
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.beginPath()
  ctx.arc(0, -2, 16, Math.PI * 0.15, Math.PI * 0.85)
  ctx.stroke()

  // 吊坠
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.moveTo(0, 16)
  ctx.lineTo(-5, 8)
  ctx.quadraticCurveTo(0, 5, 5, 8)
  ctx.closePath()
  ctx.fill()
  ctx.strokeStyle = darken(color, 30)
  ctx.lineWidth = 1.2
  ctx.stroke()

  // 吊坠高光
  ctx.fillStyle = 'rgba(255, 255, 255, 0.4)'
  ctx.beginPath()
  ctx.ellipse(-1, 10, 1.5, 2.5, -0.3, 0, Math.PI * 2)
  ctx.fill()

  ctx.restore()
}

/**
 * 绘制帽子 — 更精致
 */
function drawHat(ctx) {
  const garment = categorizedGarments.value['帽子']
  const color = getGarmentColor(garment)
  const outlineColor = darken(color, 30)

  ctx.save()
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  // 帽身
  ctx.beginPath()
  ctx.moveTo(-32, -74)
  ctx.quadraticCurveTo(-34, -105, 0, -112)
  ctx.quadraticCurveTo(34, -105, 32, -74)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 帽檐 — 更有层次
  ctx.fillStyle = darken(color, 10)
  ctx.beginPath()
  ctx.ellipse(0, -74, 44, 10, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.strokeStyle = outlineColor
  ctx.stroke()

  // 帽子装饰带
  ctx.fillStyle = darken(color, 25)
  ctx.beginPath()
  ctx.moveTo(-32, -80)
  ctx.quadraticCurveTo(0, -86, 32, -80)
  ctx.quadraticCurveTo(0, -82, -32, -80)
  ctx.closePath()
  ctx.fill()

  // 帽子高光
  ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
  ctx.beginPath()
  ctx.ellipse(-10, -95, 12, 8, -0.3, 0, Math.PI * 2)
  ctx.fill()

  ctx.restore()
}

/**
 * 绘制头发 — 分层：内层深色 + 外层主色 + 高光条纹
 */
function drawHair(ctx) {
  const color = hairColor.value
  const hairId = props.avatarConfig?.hair_id || 1

  ctx.save()
  switch (hairId) {
    case 1: drawHairShort(ctx, color); break
    case 2: drawHairLong(ctx, color); break
    case 3: drawHairBlonde(ctx, color); break
    case 4: drawHairRed(ctx, color); break
    case 5: drawHairPurple(ctx, color); break
    default: drawHairShort(ctx, color)
  }
  ctx.restore()
}

/**
 * 短发 — 有层次感
 */
function drawHairShort(ctx, color) {
  const deepColor = darken(color, 35)
  const outlineColor = darken(color, 45)

  // 内层深色阴影
  ctx.fillStyle = deepColor
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  ctx.beginPath()
  ctx.moveTo(0, -85)
  ctx.bezierCurveTo(38, -85, 42, -58, 38, -42)
  ctx.lineTo(34, -42)
  ctx.quadraticCurveTo(36, -60, 0, -70)
  ctx.quadraticCurveTo(-36, -60, -34, -42)
  ctx.lineTo(-38, -42)
  ctx.bezierCurveTo(-42, -58, -38, -85, 0, -85)
  ctx.closePath()
  ctx.fill()

  // 外层主色 — 头发主体
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  // 头顶
  ctx.beginPath()
  ctx.moveTo(0, -88)
  ctx.bezierCurveTo(40, -88, 44, -60, 40, -40)
  ctx.lineTo(36, -40)
  ctx.quadraticCurveTo(38, -58, 0, -72)
  ctx.quadraticCurveTo(-38, -58, -36, -40)
  ctx.lineTo(-40, -40)
  ctx.bezierCurveTo(-44, -60, -40, -88, 0, -88)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 刘海 — 有层次的分组
  const bangs = [
    { x: -20, w: 14, h: 22, tipY: -32 },
    { x: -6, w: 13, h: 26, tipY: -28 },
    { x: 8, w: 13, h: 24, tipY: -30 },
    { x: 22, w: 12, h: 20, tipY: -34 },
  ]
  for (const b of bangs) {
    ctx.beginPath()
    ctx.moveTo(b.x - b.w / 2, -58)
    ctx.quadraticCurveTo(b.x - b.w / 2 - 3, -58 + b.h * 0.6, b.x, b.tipY)
    ctx.quadraticCurveTo(b.x + b.w / 2 + 3, -58 + b.h * 0.6, b.x + b.w / 2, -58)
    ctx.closePath()
    ctx.fill()
    ctx.stroke()
  }

  // 侧面头发
  ctx.fillStyle = color
  // 左侧
  ctx.beginPath()
  ctx.moveTo(-38, -50)
  ctx.quadraticCurveTo(-42, -30, -36, -18)
  ctx.quadraticCurveTo(-34, -12, -30, -10)
  ctx.lineTo(-28, -38)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
  // 右侧
  ctx.beginPath()
  ctx.moveTo(38, -50)
  ctx.quadraticCurveTo(42, -30, 36, -18)
  ctx.quadraticCurveTo(34, -12, 30, -10)
  ctx.lineTo(28, -38)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 高光条纹
  ctx.fillStyle = 'rgba(255, 255, 255, 0.18)'
  ctx.beginPath()
  ctx.ellipse(-12, -78, 8, 14, -0.15, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(10, -75, 6, 12, 0.1, 0, Math.PI * 2)
  ctx.fill()
}

/**
 * 长发 — 有层次感
 */
function drawHairLong(ctx, color) {
  const deepColor = darken(color, 35)
  const outlineColor = darken(color, 45)

  // 内层深色
  ctx.fillStyle = deepColor
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  // 左侧长发内层
  ctx.beginPath()
  ctx.moveTo(-38, -50)
  ctx.quadraticCurveTo(-44, -15, -40, 42)
  ctx.quadraticCurveTo(-38, 52, -30, 50)
  ctx.quadraticCurveTo(-34, 15, -30, -20)
  ctx.closePath()
  ctx.fill()
  // 右侧长发内层
  ctx.beginPath()
  ctx.moveTo(38, -50)
  ctx.quadraticCurveTo(44, -15, 40, 42)
  ctx.quadraticCurveTo(38, 52, 30, 50)
  ctx.quadraticCurveTo(34, 15, 30, -20)
  ctx.closePath()
  ctx.fill()

  // 外层主色
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor

  // 左侧长发
  ctx.beginPath()
  ctx.moveTo(-38, -50)
  ctx.quadraticCurveTo(-46, -15, -42, 45)
  ctx.quadraticCurveTo(-40, 56, -32, 54)
  ctx.quadraticCurveTo(-36, 18, -30, -20)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 右侧长发
  ctx.beginPath()
  ctx.moveTo(38, -50)
  ctx.quadraticCurveTo(46, -15, 42, 45)
  ctx.quadraticCurveTo(40, 56, 32, 54)
  ctx.quadraticCurveTo(36, 18, 30, -20)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 头顶
  ctx.beginPath()
  ctx.moveTo(0, -88)
  ctx.bezierCurveTo(40, -88, 44, -60, 38, -42)
  ctx.lineTo(-38, -42)
  ctx.bezierCurveTo(-44, -60, -40, -88, 0, -88)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 刘海
  const bangs = [
    { x: -22, w: 15, h: 24, tipY: -30 },
    { x: -8, w: 14, h: 28, tipY: -26 },
    { x: 6, w: 14, h: 26, tipY: -28 },
    { x: 20, w: 14, h: 22, tipY: -32 },
  ]
  for (const b of bangs) {
    ctx.beginPath()
    ctx.moveTo(b.x - b.w / 2, -56)
    ctx.quadraticCurveTo(b.x - b.w / 2 - 2, -56 + b.h * 0.6, b.x, b.tipY)
    ctx.quadraticCurveTo(b.x + b.w / 2 + 2, -56 + b.h * 0.6, b.x + b.w / 2, -56)
    ctx.closePath()
    ctx.fill()
  }

  // 长发高光
  ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
  ctx.beginPath()
  ctx.ellipse(-38, 10, 4, 22, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(38, 10, 4, 22, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(-10, -78, 7, 12, -0.1, 0, Math.PI * 2)
  ctx.fill()
}

/**
 * 金色波浪短发
 */
function drawHairBlonde(ctx, color) {
  const deepColor = darken(color, 35)
  const outlineColor = darken(color, 45)

  // 外层 — 蓬松波浪
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  ctx.beginPath()
  ctx.moveTo(0, -90)
  // 右侧蓬松
  ctx.bezierCurveTo(42, -90, 48, -60, 42, -38)
  // 波浪边缘
  ctx.quadraticCurveTo(38, -25, 32, -18)
  ctx.quadraticCurveTo(28, -26, 22, -32)
  ctx.quadraticCurveTo(16, -22, 10, -36)
  ctx.quadraticCurveTo(5, -24, 0, -38)
  ctx.quadraticCurveTo(-5, -24, -10, -36)
  ctx.quadraticCurveTo(-16, -22, -22, -32)
  ctx.quadraticCurveTo(-28, -26, -32, -18)
  ctx.quadraticCurveTo(-38, -25, -42, -38)
  // 左侧蓬松
  ctx.bezierCurveTo(-48, -60, -42, -90, 0, -90)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 内层深色
  ctx.fillStyle = deepColor
  ctx.beginPath()
  ctx.moveTo(0, -88)
  ctx.bezierCurveTo(36, -88, 40, -60, 36, -42)
  ctx.quadraticCurveTo(32, -50, 0, -62)
  ctx.quadraticCurveTo(-32, -50, -36, -42)
  ctx.bezierCurveTo(-40, -60, -36, -88, 0, -88)
  ctx.closePath()
  ctx.fill()

  // 高光
  ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'
  ctx.beginPath()
  ctx.ellipse(-14, -76, 10, 14, -0.2, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(12, -72, 7, 10, 0.15, 0, Math.PI * 2)
  ctx.fill()
}

/**
 * 红色双马尾
 */
function drawHairRed(ctx, color) {
  const deepColor = darken(color, 35)
  const outlineColor = darken(color, 45)

  // 头顶
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  ctx.beginPath()
  ctx.moveTo(0, -88)
  ctx.bezierCurveTo(38, -88, 42, -60, 38, -42)
  ctx.lineTo(-38, -42)
  ctx.bezierCurveTo(-42, -60, -38, -88, 0, -88)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 刘海
  const bangs = [
    { x: -20, w: 14, h: 22, tipY: -32 },
    { x: -5, w: 12, h: 26, tipY: -28 },
    { x: 10, w: 13, h: 24, tipY: -30 },
    { x: 23, w: 11, h: 20, tipY: -34 },
  ]
  for (const b of bangs) {
    ctx.beginPath()
    ctx.moveTo(b.x - b.w / 2, -56)
    ctx.quadraticCurveTo(b.x - b.w / 2 - 2, -56 + b.h * 0.6, b.x, b.tipY)
    ctx.quadraticCurveTo(b.x + b.w / 2 + 2, -56 + b.h * 0.6, b.x + b.w / 2, -56)
    ctx.closePath()
    ctx.fill()
  }

  // 左马尾
  drawPonytail(ctx, -32, -44, -44, 22, color, deepColor)
  // 右马尾
  drawPonytail(ctx, 32, -44, 44, 22, color, deepColor)

  // 头顶高光
  ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
  ctx.beginPath()
  ctx.ellipse(-8, -78, 8, 10, -0.1, 0, Math.PI * 2)
  ctx.fill()
}

/**
 * 紫色齐刘海长发
 */
function drawHairPurple(ctx, color) {
  const deepColor = darken(color, 35)
  const outlineColor = darken(color, 45)

  // 内层
  ctx.fillStyle = deepColor
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2

  ctx.beginPath()
  ctx.moveTo(-38, -50)
  ctx.quadraticCurveTo(-44, -15, -40, 50)
  ctx.quadraticCurveTo(-38, 58, -30, 56)
  ctx.quadraticCurveTo(-34, 18, -30, -20)
  ctx.closePath()
  ctx.fill()
  ctx.beginPath()
  ctx.moveTo(38, -50)
  ctx.quadraticCurveTo(44, -15, 40, 50)
  ctx.quadraticCurveTo(38, 58, 30, 56)
  ctx.quadraticCurveTo(34, 18, 30, -20)
  ctx.closePath()
  ctx.fill()

  // 外层主色 — 左侧
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.moveTo(-38, -50)
  ctx.quadraticCurveTo(-46, -15, -42, 52)
  ctx.quadraticCurveTo(-40, 62, -32, 60)
  ctx.quadraticCurveTo(-36, 20, -30, -20)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 右侧
  ctx.beginPath()
  ctx.moveTo(38, -50)
  ctx.quadraticCurveTo(46, -15, 42, 52)
  ctx.quadraticCurveTo(40, 62, 32, 60)
  ctx.quadraticCurveTo(36, 20, 30, -20)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 头顶
  ctx.beginPath()
  ctx.moveTo(0, -88)
  ctx.bezierCurveTo(40, -88, 44, -60, 38, -42)
  ctx.lineTo(-38, -42)
  ctx.bezierCurveTo(-44, -60, -40, -88, 0, -88)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 齐刘海 — 整齐的平刘海
  ctx.beginPath()
  ctx.moveTo(-36, -56)
  ctx.lineTo(-36, -48)
  ctx.lineTo(36, -48)
  ctx.lineTo(36, -56)
  ctx.quadraticCurveTo(36, -62, 20, -65)
  ctx.quadraticCurveTo(0, -68, -20, -65)
  ctx.quadraticCurveTo(-36, -62, -36, -56)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 刘海高光
  ctx.fillStyle = 'rgba(255, 255, 255, 0.18)'
  ctx.beginPath()
  ctx.ellipse(-10, -56, 8, 4, 0, 0, Math.PI * 2)
  ctx.fill()

  // 长发高光
  ctx.fillStyle = 'rgba(255, 255, 255, 0.12)'
  ctx.beginPath()
  ctx.ellipse(-38, 15, 4, 25, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(38, 15, 4, 25, 0, 0, Math.PI * 2)
  ctx.fill()
}

/**
 * 绘制马尾辫 — 有层次
 */
function drawPonytail(ctx, startX, startY, offsetX, length, color, deepColor) {
  const outlineColor = darken(color, 45)
  ctx.save()

  // 发绳
  ctx.fillStyle = darken(color, 20)
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 1.5
  ctx.beginPath()
  ctx.ellipse(startX, startY, 5, 4, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()

  // 马尾内层深色
  if (deepColor) {
    ctx.fillStyle = deepColor
    ctx.beginPath()
    ctx.moveTo(startX - 3, startY)
    ctx.quadraticCurveTo(offsetX - 8, startY + length / 2, offsetX - 4, startY + length)
    ctx.quadraticCurveTo(offsetX, startY + length + 8, offsetX + 4, startY + length)
    ctx.quadraticCurveTo(offsetX + 8, startY + length / 2, startX + 3, startY)
    ctx.closePath()
    ctx.fill()
  }

  // 马尾外层
  ctx.fillStyle = color
  ctx.strokeStyle = outlineColor
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(startX - 4, startY)
  ctx.quadraticCurveTo(offsetX - 10, startY + length / 2, offsetX - 6, startY + length)
  ctx.quadraticCurveTo(offsetX, startY + length + 12, offsetX + 6, startY + length)
  ctx.quadraticCurveTo(offsetX + 10, startY + length / 2, startX + 4, startY)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 马尾高光
  ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
  ctx.beginPath()
  ctx.ellipse(offsetX - 2, startY + length * 0.4, 3, 10, 0.1, 0, Math.PI * 2)
  ctx.fill()

  ctx.restore()
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

/**
 * 颜色变亮
 */
function lighten(hex, amount) {
  let color = hex.replace('#', '')
  if (color.length === 3) {
    color = color[0] + color[0] + color[1] + color[1] + color[2] + color[2]
  }
  const r = Math.min(255, parseInt(color.substring(0, 2), 16) + amount)
  const g = Math.min(255, parseInt(color.substring(2, 4), 16) + amount)
  const b = Math.min(255, parseInt(color.substring(4, 6), 16) + amount)
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
