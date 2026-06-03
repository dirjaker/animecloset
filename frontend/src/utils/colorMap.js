/**
 * 颜色映射工具
 * 将中文颜色名映射到十六进制色值
 * 用于从服装 tags.color 中解析颜色
 */

// 中文颜色名 → 十六进制色值
const COLOR_MAP = {
  '黑色': '#000000',
  '白色': '#FFFFFF',
  '红色': '#FF0000',
  '蓝色': '#4A90D9',
  '天蓝': '#87CEEB',
  '深蓝': '#1A3A5C',
  '绿色': '#27AE60',
  '浅绿': '#90EE90',
  '深绿': '#006400',
  '黄色': '#F1C40F',
  '紫色': '#9B59B6',
  '浅紫': '#D7BDE2',
  '灰色': '#95A5A6',
  '深灰': '#636E72',
  '浅灰': '#BDC3C7',
  '粉色': '#FFB6C1',
  '粉红': '#FF69B4',
  '橙色': '#E67E22',
  '棕色': '#8B4513',
  '咖啡': '#6F4E37',
  '米色': '#F5DEB3',
  '卡其': '#C3B091',
  '酒红': '#722F37',
  '玫红': '#FF007F',
  '青色': '#00CED1',
  '藏青': '#003153',
  '驼色': '#C19A6B',
  '杏色': '#FBCEB1',
  '金色': '#FFD700',
  '银色': '#C0C0C0',
}

// 默认颜色（当无法匹配时使用）
const DEFAULT_COLOR = '#95A5A6'

/**
 * 根据中文颜色名获取十六进制色值
 * @param {string} colorName - 中文颜色名
 * @returns {string} 十六进制颜色值
 */
export function getColorByName(colorName) {
  if (!colorName) return DEFAULT_COLOR
  // 精确匹配
  if (COLOR_MAP[colorName]) return COLOR_MAP[colorName]
  // 模糊匹配：检查颜色名是否包含在映射中
  for (const [key, value] of Object.entries(COLOR_MAP)) {
    if (colorName.includes(key) || key.includes(colorName)) {
      return value
    }
  }
  // 如果已经是十六进制格式，直接返回
  if (/^#[0-9A-Fa-f]{6}$/.test(colorName)) return colorName
  return DEFAULT_COLOR
}

// 服装类别默认颜色
const CATEGORY_COLORS = {
  '上衣': '#E879F9',   // 粉紫
  '下装': '#60A5FA',   // 蓝色
  '外套': '#A78BFA',   // 紫色
  '鞋子': '#F97316',   // 橙色
  '配饰': '#FBBF24',   // 金色
  '连衣裙': '#F472B6', // 粉色
  '袜子': '#E9D5FF',   // 浅紫
  '帽子': '#34D399',   // 绿色
  '包': '#FCD34D',     // 黄色
}

/**
 * 根据服装类别获取默认颜色
 * @param {string} category - 服装类别
 * @returns {string} 十六进制颜色值
 */
export function getCategoryColor(category) {
  return CATEGORY_COLORS[category] || DEFAULT_COLOR
}

/**
 * 从 garment 对象中获取颜色
 * 优先从 tags.color 解析，其次使用类别默认色
 * @param {Object} garment - 服装对象
 * @returns {string} 十六进制颜色值
 */
export function getGarmentColor(garment) {
  if (!garment) return DEFAULT_COLOR
  // 尝试从 tags 中获取颜色
  const tags = garment.tags || {}
  if (tags.color) {
    return getColorByName(tags.color)
  }
  // 尝试从字段中直接获取颜色
  if (garment.color) {
    return getColorByName(garment.color)
  }
  // 使用类别默认色
  return getCategoryColor(garment.category)
}

// 肤色映射
export const SKIN_COLORS = {
  1: '#FFE0BD',
  2: '#F5D0A9',
  3: '#D4A574',
  4: '#C68642',
  5: '#8D5524',
}

// 发色映射
export const HAIR_COLORS = {
  1: '#2C2C2C',  // 黑色
  2: '#8B4513',  // 棕色
  3: '#DAA520',  // 金色
  4: '#FF6B6B',  // 红色
  5: '#9B59B6',  // 紫色
}

// 瞳色映射
export const EYE_COLORS = {
  brown: '#8B4513',
  blue: '#4A90D9',
  green: '#27AE60',
  purple: '#9B59B6',
  red: '#FF6B6B',
}
