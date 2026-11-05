#!/usr/bin/env bash
# lint_design.sh — 检查常见 AI 味与违规项
# 用法: bash lint_design.sh <项目目录>

set -euo pipefail

TARGET="${1:-.}"
if [[ ! -d "$TARGET" ]]; then
  echo "错误: 目录不存在: $TARGET" >&2
  exit 1
fi

echo "=== Design Lint Report ==="
echo "扫描目录: $TARGET"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

VIOLATIONS=0

# 1. 紫蓝渐变
echo "--- [1] 紫蓝渐变检查 ---"
if grep -rn --include="*.css" --include="*.scss" --include="*.html" --include="*.jsx" --include="*.tsx" \
  -E "linear-gradient.*#[6-8][0-9a-fA-F]{5}" "$TARGET" 2>/dev/null; then
  echo "❌ 发现紫蓝渐变（#6366f1 / #8b5cf6 系），参考 anti-patterns.md ✗1"
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ 通过"
fi
echo ""

# 2. 默认字体（未指定具体字体族）
echo "--- [2] 默认字体检查 ---"
if grep -rn --include="*.css" --include="*.scss" \
  -E "font-family\s*:\s*['\"]?(sans-serif|serif|monospace)['\"]?\s*;" "$TARGET" 2>/dev/null | \
  grep -v -E "(Inter|Roboto|system-ui|-apple-system|PingFang|Hiragino)" | head -5; then
  echo "❌ 发现裸 font-family（仅 sans-serif/serif/monospace，无具体字体），参考 tokens-and-type.md §2.2"
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ 通过"
fi
echo ""

# 3. emoji 图标
echo "--- [3] Emoji 图标检查 ---"
if grep -rn --include="*.html" --include="*.jsx" --include="*.tsx" --include="*.vue" \
  -P "[😀-🙏🚀-🛿]" "$TARGET" 2>/dev/null | head -5; then
  echo "❌ 发现 emoji 图标，应替换为 Lucide 或 SVG 图标"
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ 通过"
fi
echo ""

# 4. 统一圆角（全站只用一个值，无层次）
echo "--- [4] 统一圆角检查 ---"
# 匹配直接 px 值和 CSS 变量定义中的 px 值（如 --radius-control: 6px）
RADIUS_VALUES=$(grep -rh --include="*.css" --include="*.scss" \
  -oE "(border-radius|--radius-[a-z]+)\s*[:]\s*[0-9]+px" "$TARGET" 2>/dev/null | \
  grep -oE "[0-9]+px" | sort -u || true)
RADIUS_COUNT=$(echo "$RADIUS_VALUES" | grep -c . || true)
RADIUS_COUNT=${RADIUS_COUNT:-0}
# 也检查 var(--radius-*) 的使用（间接双档）
RADIUS_VAR_COUNT=$(grep -rh --include="*.css" --include="*.scss" \
  -oE "var\(--radius-[a-z]+\)" "$TARGET" 2>/dev/null | sort -u | wc -l || true)
RADIUS_VAR_COUNT=${RADIUS_VAR_COUNT:-0}
if [[ "$RADIUS_COUNT" -eq 1 && "$RADIUS_VAR_COUNT" -eq 0 ]]; then
  echo "❌ 全站只用一个圆角值，缺少层次（应分控件/卡片两档），参考 tokens-and-type.md §5.1"
  VIOLATIONS=$((VIOLATIONS + 1))
elif [[ "$RADIUS_COUNT" -eq 0 && "$RADIUS_VAR_COUNT" -eq 0 ]]; then
  echo "⚠️  未检测到 border-radius（可能用 Tailwind 类名，需手动确认双档制）"
else
  echo "✓ 通过（px 值 $RADIUS_COUNT 种 + CSS 变量 $RADIUS_VAR_COUNT 种）"
fi
echo ""

# 5. 纯白底（#fff 或 rgb(255,255,255)）
echo "--- [5] 纯白底检查 ---"
if grep -rn --include="*.css" --include="*.scss" \
  -E "(background|background-color)\s*:\s*(#fff\b|#ffffff\b|rgb\(255,\s*255,\s*255\))" "$TARGET" 2>/dev/null | \
  head -5; then
  echo "❌ 发现纯白底 #fff/#ffffff，应使用暖白（如 #faf9f6），参考 tokens-and-type.md §3.1"
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ 通过"
fi
echo ""

# 6. 纯黑字（#000 或 rgb(0,0,0)）
echo "--- [6] 纯黑字检查 ---"
if grep -rn --include="*.css" --include="*.scss" \
  -E "color\s*:\s*(#000\b|#000000\b|rgb\(0,\s*0,\s*0\))" "$TARGET" 2>/dev/null | \
  head -5; then
  echo "❌ 发现纯黑字 #000/#000000，应使用近黑（如 #08090a），参考 tokens-and-type.md §3.3"
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ 通过"
fi
echo ""

# 7. 玻璃拟态（backdrop-filter blur）
echo "--- [7] 玻璃拟态检查 ---"
BLUR_COUNT=$(grep -rc --include="*.css" --include="*.scss" "backdrop-filter.*blur" "$TARGET" 2>/dev/null | \
  awk -F: '{sum += $2} END {print sum+0}' || true)
BLUR_COUNT=${BLUR_COUNT:-0}
if [[ "$BLUR_COUNT" -gt 3 ]]; then
  echo "❌ 发现 $BLUR_COUNT 处 backdrop-filter blur，大面积使用会影响性能，参考 anti-patterns.md ✗3"
  VIOLATIONS=$((VIOLATIONS + 1))
elif [[ "$BLUR_COUNT" -gt 0 ]]; then
  echo "⚠️  发现 $BLUR_COUNT 处 backdrop-filter blur（≤3 可接受，需确认仅局部用）"
else
  echo "✓ 通过"
fi
echo ""

# 8. 滚动劫持（body position: fixed）
echo "--- [8] 滚动劫持检查 ---"
if grep -rn --include="*.css" --include="*.scss" --include="*.js" --include="*.ts" \
  -E "(body|html)\s*\{[^}]*position\s*:\s*fixed" "$TARGET" 2>/dev/null; then
  echo "❌ 发现 body/html position:fixed 滚动劫持，参考 motion.md §4.1"
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ 通过"
fi
echo ""

# 9. 全大写 + 负字距（作品集腔）
echo "--- [9] 全大写 + 负字距检查 ---"
if grep -rn --include="*.css" --include="*.scss" \
  -E "text-transform\s*:\s*uppercase.*letter-spacing\s*:\s*-0\.[0-9][3-9]" "$TARGET" 2>/dev/null || \
   grep -rn --include="*.css" --include="*.scss" \
  -E "letter-spacing\s*:\s*-0\.[0-9][3-9].*text-transform\s*:\s*uppercase" "$TARGET" 2>/dev/null; then
  echo "❌ 发现全大写 + 负字距 > -0.03em，CJK 项目禁止，参考 anti-patterns.md ✗4"
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ 通过"
fi
echo ""

# 总结
echo "=========================="
if [[ "$VIOLATIONS" -eq 0 ]]; then
  echo "✅ 全部通过，无违规项"
  exit 0
else
  echo "❌ 发现 $VIOLATIONS 类违规项，需修正或在 Design Brief 中说明保留理由"
  exit 1
fi
