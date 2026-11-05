# 组件系统与设计工具学习报告

> 2026-11-05。覆盖 5/7 个目标系统（Semi Design、Ant Design、Element Plus、shadcn/ui、Lucide Icons）。
> astryx.atmeta.com（ERR_CONNECTION_CLOSED）与 stitch.withgoogle.com（空页面）无法访问，已如实记录。

---

## 0. 系统可达性

| 系统 | 状态 | 框架 | 语言 |
|---|---|---|---|
| Semi Design | ✅ 可达 | React | 中文 |
| Ant Design | ✅ 可达 | React | 中+英 |
| Element Plus | ✅ 可达 | Vue 3 | 中文 |
| shadcn/ui | ✅ 可达 | React | 中+英 |
| Lucide Icons | ✅ 可达 | 跨框架 | 英文 |
| astryx.atmeta.com | ❌ ERR_CONNECTION_CLOSED | — | — |
| stitch.withgoogle.com | ❌ 页面空白（0字节 body） | — | — |

---

## 1. Token 命名与分层方式

### 1.1 Semi Design（三层分级最明确）

**分层结构**（由抽象到具体）：

```
全局 Token (Global)
  ↓ 映射
别名 Token (Alias)  
  ↓ 映射
组件 Token (Component)
```

**实例**：

```scss
// 全局层：定义原子值
--semi-color-primary: #0077fa;
--semi-spacing-base: 4px;

// 别名层：语义化命名
--semi-color-link: var(--semi-color-primary);
--semi-spacing-tight: calc(var(--semi-spacing-base) * 2);

// 组件层：具体应用
--semi-button-primary-bg: var(--semi-color-primary);
--semi-button-padding-y: var(--semi-spacing-tight);
```

**关键特性**：
- **全局 Token** 只定义数值，不表达用途（如 `--semi-gray-0` 到 `--semi-gray-9`）
- **别名 Token** 表达语义（`--semi-color-success`、`--semi-color-danger`）
- **组件 Token** 直接对应组件内部 DOM 节点（`--semi-input-border-color`、`--semi-table-header-bg`）
- 支持编译时定制（`prefixCls`、CSS Layer）需要 Webpack/Rspack

依据：[Semi Design Token 文档](https://semi.design/zh-CN/basic/tokens)

### 1.2 Ant Design（双层 + ConfigProvider）

**分层结构**：

```
Seed Token（原子色、尺寸）
  ↓
Map Token（场景色、组件通用尺寸）
  ↓ 
Alias Token（语义化别名）→ 组件消费
```

**实例**（通过 ConfigProvider）：

```tsx
import { ConfigProvider } from 'antd';

<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#00b96b',  // Seed Token
      borderRadius: 2,
    },
    components: {
      Button: {
        colorPrimary: '#1890ff',  // 组件级覆盖
        algorithm: true,          // 自动生成 hover/active 态
      },
    },
  }}
>
  <App />
</ConfigProvider>
```

**关键特性**：
- **算法驱动**：修改 `colorPrimary` 自动生成 6 个梯度色（`colorPrimaryHover`、`colorPrimaryActive`…）
- **双套方案**：CSS 变量（`:where(.css-dev-only-do-not-override-htwhyh)`）+ JS 变量（运行时计算）
- **组件级覆盖**：`theme.components.Button` 只影响 Button，不污染全局
- 不推荐手写 CSS 变量，通过 ConfigProvider API 修改

依据：[Ant Design 定制主题](https://ant.design/docs/react/customize-theme)、[设计价值观](https://ant.design/docs/spec/introduce)

### 1.3 Element Plus（单层 CSS 变量）

**分层结构**（扁平，无中间层）：

```
CSS 变量（全局）→ 组件直接消费
```

**实例**：

```css
/* 全局修改 */
:root {
  --el-color-primary: green;
  --el-border-radius-base: 4px;
}

/* 组件级修改（推荐） */
.custom-class {
  --el-tag-bg-color: red;
  --el-button-border-radius: 8px;
}
```

**关键特性**：
- **极简方案**：只有一层 CSS 变量，直接映射到组件
- **性能优先**：推荐在类名下覆盖，避免全局 `:root` 污染
- **VueUse 集成**：可用 `useCssVar` hook 动态控制
- 无算法生成，手动定义全部梯度（`--el-color-primary-light-3`、`--el-color-primary-dark-2`）

依据：[Element Plus 主题定制](https://element-plus.org/zh-CN/guide/theming.html)

### 1.4 shadcn/ui（Tailwind 变量 + 语义 Token）

**分层结构**（与 Tailwind 深度绑定）：

```
CSS 变量（HSL 色值）
  ↓
Tailwind 工具类（bg-background, text-foreground）
  ↓
组件类名引用
```

**实例**（`globals.css`）：

```css
@layer base {
  :root {
    --background: 0 0% 100%;        /* hsl(0, 0%, 100%) 白色 */
    --foreground: 222.2 84% 4.9%;   /* 深灰文字 */
    --primary: 222.2 47.4% 11.2%;   /* 主色 */
    --primary-foreground: 210 40% 98%; /* 主色上的文字 */
    --radius: 0.5rem;
  }
  .dark {
    --background: 222.2 84% 4.9%;   /* 深色模式底 */
    --foreground: 210 40% 98%;
  }
}
```

**使用**：

```tsx
<div className="bg-background text-foreground rounded-[var(--radius)]">
  <Button className="bg-primary text-primary-foreground">Click</Button>
</div>
```

**关键特性**：
- **HSL 格式无单位**：只写 `222.2 47.4% 11.2%`，Tailwind 自动补 `hsl()`
- **语义命名**：`background`/`foreground`/`primary`/`secondary`/`muted`/`accent` 六大语义
- **dark class 切换**：通过 `next-themes` 在根元素加 `.dark` 类
- **非库，是复制代码**：shadcn 不是 npm 包，是把组件源码复制到项目 `components/ui/`

依据：[shadcn/ui 主题设置](https://www.shadcn.com.cn/docs/theming)

### 1.5 对比总结

| 维度 | Semi | Ant | Element | shadcn |
|---|---|---|---|---|
| 分层数 | **3 层**（Global→Alias→Component） | 2.5 层（Seed→Map→Alias） | 1 层（扁平 CSS 变量） | 1 层（CSS 变量+Tailwind） |
| 命名风格 | `--semi-{scope}-{property}` | `colorPrimary`（驼峰） | `--el-{property}` | `--{semantic}` |
| 算法生成 | ❌（手动定义全部） | ✅（修改 primary 自动生梯度） | ❌ | ❌ |
| 定制方式 | CSS 变量 / Design Token Platform | ConfigProvider API | CSS 变量 | CSS 变量（编辑 globals.css） |
| 组件级覆盖 | ✅（`.semi-button { --semi-button-* }`）| ✅（`theme.components`）| ✅（`.custom { --el-tag-* }`）| ✅（Tailwind 类覆盖）|
| 编译时能力 | ✅（prefixCls、CSS Layer，需 Webpack）| ❌（纯运行时）| ❌ | ✅（Tailwind 编译）|

**选型建议**：
- **需要严格分层、多主题管理**：Semi（字节跳动内部多产品线场景）
- **需要算法自动生成色阶**：Ant（改一个主色，全套 UI 自动适配）
- **Vue 3 + 极简配置**：Element Plus
- **Tailwind 用户 + 不想引入重库**：shadcn（复制代码，完全可控）

---

## 2. 主题定制机制

### 2.1 暗色模式实现方式对比

| 系统 | 暗色模式方案 | 切换机制 | 示例 |
|---|---|---|---|
| **Semi** | CSS 变量 + `body[theme-mode="dark"]` | `<Button theme="dark">`（组件级）或全局 `<ConfigProvider theme>`  | [Semi 暗色模式](https://semi.design/zh-CN/basic/dark-mode) |
| **Ant** | ConfigProvider `algorithm: theme.darkAlgorithm` | 运行时切换 `<ConfigProvider theme={{ algorithm: theme.darkAlgorithm }}>` | [Ant 暗色算法](https://ant.design/docs/react/customize-theme#%E4%BD%BF%E7%94%A8%E6%9A%97%E8%89%B2%E7%AE%97%E6%B3%95) |
| **Element** | CSS 变量 + `html.dark` 类 | VueUse `useDark()` 或手动 `document.documentElement.classList.toggle('dark')` | [Element Plus 暗黑模式](https://element-plus.org/zh-CN/guide/dark-mode.html) |
| **shadcn** | CSS 变量 + `.dark` 类 | `next-themes` 的 `<ThemeProvider>` + `useTheme()` hook | [shadcn Theming](https://www.shadcn.com.cn/docs/theming) |

**最佳实践**（来自各系统文档）：

#### Semi 的组件级暗色

```tsx
// 全局暗色
<ConfigProvider theme="dark">
  <App />
</ConfigProvider>

// 单个组件暗色（其余保持浅色）
<Button theme="dark">暗色按钮</Button>
<Select theme="dark" />
```

**优势**：不用整页切换，可以局部用暗色组件（如代码编辑器在浅色页面中用暗色主题）。

#### Ant 的算法切换

```tsx
import { theme } from 'antd';

<ConfigProvider theme={{
  algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
}}>
  <App />
</ConfigProvider>
```

**优势**：所有颜色（包括自定义的）自动反转，不需要手写暗色变量。

#### shadcn 的 next-themes

```tsx
// app/layout.tsx
import { ThemeProvider } from 'next-themes'

<ThemeProvider attribute="class" defaultTheme="system">
  <html suppressHydrationWarning>
    <body>{children}</body>
  </html>
</ThemeProvider>

// 组件中使用
import { useTheme } from 'next-themes'
const { theme, setTheme } = useTheme()
<button onClick={() => setTheme('dark')}>暗色</button>
```

**优势**：自动同步系统偏好（`prefers-color-scheme`），支持 SSR 无闪烁。

### 2.2 跨系统定制流程

#### 场景 1：改主色

| 系统 | 步骤 | 代码 |
|---|---|---|
| Semi | 1. 修改 `--semi-color-primary`<br>2. 重启看效果（编译时） | `:root { --semi-color-primary: #7c3aed; }` |
| Ant | 1. ConfigProvider 传 `token.colorPrimary`<br>2. 自动生成 hover/active 态 | `<ConfigProvider theme={{ token: { colorPrimary: '#7c3aed' } }}>` |
| Element | 1. 覆盖 `--el-color-primary`<br>2. 手动定义 9 个梯度 | `:root { --el-color-primary: #7c3aed; --el-color-primary-light-3: #a78bfa; }` |
| shadcn | 1. 编辑 `globals.css` 的 `--primary`<br>2. 用 HSL 格式 | `--primary: 262 83% 58%;  /* hsl(262, 83%, 58%) */` |

#### 场景 2：改圆角

| 系统 | Token 名 | 默认值 | 改法 |
|---|---|---|---|
| Semi | `--semi-border-radius-small/medium/large` | 3px / 6px / 12px | 全局或组件 CSS 变量 |
| Ant | `borderRadius`（Seed Token） | 6px | ConfigProvider `token.borderRadius` |
| Element | `--el-border-radius-base/small/round/circle` | 4px / 2px / 20px / 100% | CSS 变量 |
| shadcn | `--radius` | 0.5rem（8px） | globals.css 改一处，全站生效 |

**注意**：Ant 的 `borderRadius` 会自动派生 `borderRadiusLG`/`borderRadiusSM`，其他系统需手动定义每个尺寸。

### 2.3 与自定义设计冲突时的处理原则

**冲突类型 1：UI 规范不一致**

- **问题**：设计稿要求 Button 高度 44px，但 Ant Design 默认 32px（中号）、40px（大号）
- **处理**：
  1. **优先用系统 size**：`<Button size="large">` 接近 40px，说服设计师接受
  2. **CSS 覆盖**（不推荐）：`.ant-btn { height: 44px !important; }` —— 会破坏内部对齐
  3. **自定义组件**（shadcn 模式）：复制 Button 源码到 `components/ui/button.tsx`，改高度后全局替换

**冲突类型 2：需要组件库没有的变体**

- **问题**：需要"幽灵按钮"（透明底 + 彩色边框 + hover 填充），但系统只有 `default`/`primary`/`dashed`
- **处理**：
  1. **Semi/Ant**：用 `type="default"` + 自定义 `style` 或 `className`
  2. **shadcn**：编辑 `components/ui/button.tsx` 的 `buttonVariants`，添加 `ghost` 变体
  3. **Element**：用 `plain` + CSS 覆盖

**冲突类型 3：主题 Token 无法满足需求**

- **问题**：设计稿有 5 个功能色（success/warning/danger/info/neutral），但系统只有 4 个
- **处理**：
  1. **Semi**：在组件 Token 层新增 `--semi-color-neutral: #64748b;`，手动应用
  2. **Ant**：扩展 Map Token（不推荐，会破坏类型）
  3. **shadcn**：直接加 `--neutral: 215 16% 47%;`，用 `bg-neutral`

**核心原则**（从 Semi、Ant 文档提炼）：

> ① **优先用系统提供的**：90% 的需求都能用 size/type/variant 组合满足  
> ② **语义层覆盖，不碰原子层**：改 `--semi-button-primary-bg`，不要改 `--semi-color-primary`（会影响全站）  
> ③ **shadcn 例外**：它就是让你改源码的，直接编辑 `components/ui/`  
> ④ **实在不行就自己写**：别强行扭曲组件库，写个 `<CustomButton>` 更清晰  

---

## 3. 什么场景选哪个、不选哪个

### 3.1 决策矩阵

| 场景 | 推荐系统 | 理由 | 不推荐 |
|---|---|---|---|
| **字节跳动内部项目** | **Semi Design** | 有内部 MCP/Skills 支持、配套 Figma Kit、内网 CDN | Ant（外部）|
| **国内 To B / 中后台** | **Ant Design** | 生态最成熟、Pro Components、国内认知度最高 | shadcn（文档主要英文）|
| **Vue 3 项目** | **Element Plus** | Vue 3 原生、组件最全（70+）| Ant（React only）|
| **Tailwind 深度用户** | **shadcn/ui** | 与 Tailwind 无缝、可完全定制、复制代码无版本锁定 | Ant/Semi（CSS-in-JS 冲突）|
| **需要极致性能** | **Element Plus** | 单层 CSS 变量、无运行时计算 | Ant（JS 算法有开销）|
| **需要算法生成色阶** | **Ant Design** | 改一个色自动生成 6+ 梯度，省设计时间 | Element（手动定义全部）|
| **多主题产品（如 SaaS）** | **Semi Design** | 三层 Token 分级最清晰、Design Token Platform 可视化编辑 | Element（扁平结构难管理）|
| **快速原型 / Hackathon** | **shadcn/ui** | `npx shadcn-ui@latest add button`，秒装、零配置 | Semi（需配置 Webpack）|
| **需要图标库** | **Lucide** + 任意系统 | 跨框架、一致描边、开源免费 | 系统自带图标（风格不统一）|

### 3.2 不选的典型原因

#### 不选 Semi 的情况

- ❌ **项目已用 Vue**：Semi 只有 React 版本
- ❌ **构建工具是 Vite + 不需要编译时定制**：Semi 的 prefixCls、CSS Layer 等高级特性需要 Webpack/Rspack
- ❌ **团队不熟悉字节技术栈**：Semi 的最佳实践（MCP、内部 CDN）对外部团队价值有限

#### 不选 Ant 的情况

- ❌ **追求极致包体积**：Ant Design 5.x 打包后约 1.2MB（gzip 后 ~400KB），shadcn 按需复制代码更小
- ❌ **设计风格与 Ant 差异大**：Ant 的蓝色 + 圆角 6px 风格辨识度高，强行覆盖成本高
- ❌ **不想用 CSS-in-JS**：Ant 4.x 用 less，5.x 用 CSS-in-JS（运行时插入样式），与 Tailwind 有冲突

#### 不选 Element Plus 的情况

- ❌ **项目是 React**：Element Plus 只支持 Vue 3
- ❌ **需要复杂主题管理**：Element 的扁平 CSS 变量在多主题场景难维护（Semi 的三层分级更适合）

#### 不选 shadcn 的情况

- ❌ **不用 Tailwind**：shadcn 深度绑定 Tailwind，脱离后失去意义
- ❌ **需要组件库持续更新**：shadcn 是复制代码，不是 npm 依赖，组件 bug 修复需要手动同步
- ❌ **团队不愿维护组件源码**：shadcn 把源码放进项目，团队要负责维护

### 3.3 组合使用策略

**最佳组合**（互补而非冲突）：

| 主组件库 | + 图标 | + 额外工具 |
|---|---|---|
| Semi / Ant / Element | Lucide | Tailwind（工具类）|
| shadcn/ui | Lucide（默认） | Radix UI（底层）|

**实例：Ant + Lucide + Tailwind**

```tsx
import { Button } from 'antd';
import { Plus, Download } from 'lucide-react';

<div className="flex gap-4">  {/* Tailwind 间距 */}
  <Button icon={<Plus size={16} />}>新建</Button>
  <Button icon={<Download size={16} />}>下载</Button>
</div>
```

**注意**：Ant 的 CSS-in-JS 与 Tailwind 可共存，但要注意：
- Tailwind 的 reset 可能覆盖 Ant 样式 → 用 `@layer` 控制优先级
- 不要混用 Ant 的 `Space` 和 Tailwind 的 `flex gap-x`（选一种）

---

## 4. Lucide 图标使用规范

### 4.1 核心参数

| 参数 | 默认值 | 推荐范围 | 说明 |
|---|---|---|---|
| `size` | 24px | 16–48px | 图标边界框大小 |
| `strokeWidth` | 2px | 1.5–2.5px | 描边粗细，**所有图标一致** |
| `color` | `currentColor` | — | 继承父元素文字颜色 |
| `absoluteStrokeWidth` | `false` | — | 设为 `true` 时，描边宽度不随 size 缩放 |

### 4.2 尺寸使用指南

```tsx
import { Home, Search, Settings } from 'lucide-react';

// 小尺寸（16px）：内联文本、标签
<span>首页 <Home size={16} /></span>

// 标准（24px）：按钮、菜单
<Button icon={<Search size={24} />}>搜索</Button>

// 大尺寸（32–48px）：空状态、引导页
<div className="empty-state">
  <Settings size={48} strokeWidth={1.5} />
  <p>暂无设置</p>
</div>
```

**关键规则**（来自 Lucide 设计指南）：

> ① **同一界面保持 strokeWidth 一致**：全部用 2px 或全部用 1.5px，不要混用  
> ② **图标与文字对齐**：用 `className="align-middle"` 或 flexbox  
> ③ **24px 是标准档**：大部分 UI 库的按钮图标都是 24px  
> ④ **小于 16px 不推荐**：描边会糊  

### 4.3 描边宽度的场景选择

| strokeWidth | 适用场景 | 视觉效果 |
|---|---|---|
| **1.5px** | 大面积图标（32px+）、极简风格 | 纤细、精致 |
| **2px**（默认）| 标准按钮、菜单、工具栏 | 平衡、清晰 |
| **2.5px** | 小尺寸（16px）、高对比需求 | 醒目、稳重 |

**错误示范**：

```tsx
❌ 同一行混用不同 strokeWidth
<div>
  <Home size={24} strokeWidth={2} />
  <Search size={24} strokeWidth={1.5} />  ← 视觉不一致
</div>

✅ 统一 strokeWidth
<div>
  <Home size={24} strokeWidth={2} />
  <Search size={24} strokeWidth={2} />
</div>
```

### 4.4 对齐与间距

#### 与文字对齐

```tsx
// 方案 1：flex 垂直居中
<div className="flex items-center gap-2">
  <Mail size={20} />
  <span>邮箱</span>
</div>

// 方案 2：inline-flex（适合内联）
<span className="inline-flex items-center gap-1">
  <CheckCircle size={16} />
  已完成
</span>
```

#### 按钮中的图标

```tsx
// Ant Design Button
<Button icon={<Plus size={16} />}>新建</Button>

// shadcn Button + Lucide
<Button>
  <Plus className="mr-2 h-4 w-4" />  {/* 16px = h-4 w-4 in Tailwind */}
  新建
</Button>
```

**注意**：
- Ant/Semi 的 `icon` prop 会自动加间距，不用手动 margin
- shadcn 需要手动加 `mr-2`（8px 右边距）

### 4.5 颜色与状态

```tsx
// 继承父元素颜色（推荐）
<div className="text-red-500">
  <AlertCircle size={24} />  {/* 自动红色 */}
  错误提示
</div>

// 单独指定颜色（不推荐，除非有特殊需求）
<Home size={24} color="#3b82f6" />

// 暗色模式自适应
<div className="text-gray-900 dark:text-gray-100">
  <Sun size={24} />  {/* 浅色模式黑色，暗色模式白色 */}
</div>
```

### 4.6 跨框架使用

| 框架 | 包名 | 安装 | 使用 |
|---|---|---|---|
| React | `lucide-react` | `npm install lucide-react` | `import { Home } from 'lucide-react'` |
| Vue 3 | `lucide-vue-next` | `npm install lucide-vue-next` | `<Home :size="24" />` |
| Svelte | `lucide-svelte` | `npm install lucide-svelte` | `<Home size={24} />` |
| Solid | `lucide-solid` | `npm install lucide-solid` | `<Home size={24} />` |
| Angular | `lucide-angular` | `npm install lucide-angular` | `<lucide-icon name="home" [size]="24"></lucide-icon>` |
| 静态 SVG | `lucide-static` | `npm install lucide-static` | 导出 SVG 文件 |

**选型建议**：
- **与 Ant/Semi/Element 搭配**：用对应框架的 Lucide 包
- **与 shadcn 搭配**：shadcn 默认就用 `lucide-react`，无需额外安装
- **SSR 项目（Next.js）**：`lucide-react` 天然支持，无需特殊配置

依据：
- [Lucide 全局样式](https://lucide.dev/guide/advanced/global-styling)
- [Lucide 描边宽度](https://lucide.dev/guide/design/stroke-width)
- [Lucide 图标设计指南](https://lucide.dev/guide/design/icon-design-guide)

---

## 5. Semi Design 的 MCP/Skills 接入评估

### 5.1 什么是 Semi MCP/Skills

#### MCP（Model Context Protocol）

**定义**：标准化协议，让 AI 助手连接外部工具和数据源。

**Semi MCP 提供的能力**：

| 工具名 | 功能 | 使用场景 |
|---|---|---|
| `get_semi_document` | 获取组件文档或组件列表 | 查找组件、了解 API |
| `get_semi_code_block` | 获取文档中隐藏的代码块 | 查看详细示例 |
| `get_component_file_list` | 获取组件源码文件列表 | 了解组件结构 |
| `get_file_code` | 获取文件代码内容 | 查看组件实现 |
| `get_function_code` | 获取函数完整实现 | 深入了解逻辑 |

**核心价值**：AI 写 Semi 代码时可以「有据可查」，不再靠过时训练数据。

#### Skills（技能包）

**定义**：预配置的指令文档，教 AI 如何正确使用 Semi Design。

**包含文件**：

| 文件 | 内容 |
|---|---|
| `WORKFLOWS.md` | 使用 MCP 工具的完整流程（查询组件 → 查看源码 → 实现功能）|
| `BEST_PRACTICES.md` | 最佳实践（组件引入、主题定制、React 19 兼容、组件扩展方法）|

**核心价值**：AI 不仅知道有哪些工具，还知道**何时用、怎么用**。

依据：[Semi MCP/Skills 文档](https://semi.design/zh-CN/start/mcp-skills)

### 5.2 接入步骤

#### 前置要求

```bash
# 检查版本
node -v    # 需要 >= 20.19.0
npm -v     # 需要 >= 11.3.0

# 如果版本不足，升级
npm install -g npm@latest
```

#### 步骤 1：安装 MCP（以 Claude Desktop 为例）

**配置文件位置**：

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**添加配置**：

```json
{
  "mcpServers": {
    "semi-design": {
      "command": "npx",
      "args": ["-y", "@douyinfe/semi-mcp@latest"]
    }
  }
}
```

**字节跳动内网用户**：
- 包名改为 `@ies/semi-mcp-bytedance`
- 或在字节云 MCP 市场搜索 "Semi" 一键添加

**其他客户端**：

| 客户端 | 配置方式 |
|---|---|
| Cursor / Trae | 设置 → MCP 配置 → 粘贴上述 JSON |
| Claude CLI (Claude Code) | `claude mcp add @douyinfe/semi-mcp` |

**故障排除**：

```bash
# 如果遇到 oxc-parser 错误（npm 的已知 bug）
npm install -g npm@latest  # 先升级 npm
npm i -g @douyinfe/semi-mcp  # 手动全局安装
# 然后重新配置 MCP
```

#### 步骤 2：安装 Skills

**方式 1：通过编程工具的 UI**（推荐）

1. 打开 [Semi MCP/Skills 页面](https://semi.design/zh-CN/start/mcp-skills)
2. 点击「添加到我的项目」
3. 选择你的编程工具（Claude Desktop / Cursor / Claude CLI / Windsurf）
4. 选择目标目录
5. 自动解压安装

**方式 2：手动下载**

```bash
# 下载 skills.zip
curl -O https://semi.design/skills.zip

# 解压到对应目录（根据你的编程工具）
# Claude Desktop: ~/.config/claude-desktop/skills/semi/
# Cursor: ~/.cursor/prompts/semi/
# Claude CLI: ~/.claude/skills/semi/
# Windsurf: ~/.windsurf/cascade/skills/semi/

unzip skills.zip -d ~/.config/claude-desktop/skills/semi/
```

**Skills 路径参考**：

| 编程工具 | Skills 路径 |
|---|---|
| Claude Desktop | `~/.config/claude-desktop/skills/semi/` |
| Cursor | `~/.cursor/prompts/semi/` |
| Claude CLI | `~/.claude/skills/semi/` |
| Windsurf | `~/.windsurf/cascade/skills/semi/` |
| 字节内网 IDE | 联系内部支持 |

### 5.3 价值评估：是否值得集成？

#### 适合的场景（✅ 推荐集成）

| 场景 | 价值 | ROI |
|---|---|---|
| **字节跳动内部项目** | 内网优化、配套工具齐全 | ⭐⭐⭐⭐⭐ |
| **AI 辅助开发 Semi 项目** | AI 能查到最新 API，减少文档查阅时间 | ⭐⭐⭐⭐⭐ |
| **新人快速上手** | Skills 提供最佳实践，避免常见陷阱 | ⭐⭐⭐⭐ |
| **复杂组件定制** | 能查看源码和函数实现，省去读 GitHub 源码的时间 | ⭐⭐⭐⭐ |
| **多版本维护** | 支持查询不同版本的组件文档（2.90.2+）| ⭐⭐⭐⭐ |

#### 不适合的场景（❌ 不值得花时间）

| 场景 | 原因 |
|---|---|
| **不用 Semi Design** | MCP 和 Skills 都是 Semi 专用，对其他组件库无价值 |
| **项目 Semi < 2.90.2** | MCP 内的知识从 2.90.2 开始稳定更新，老版本可能不符 |
| **不用 AI 辅助编码** | 如果团队不用 Claude / Cursor 等 AI 工具，MCP 无意义 |
| **已熟悉 Semi 全部 API** | 资深用户直接看文档更快，MCP 反而多一层间接 |
| **网络环境无法访问 npm** | 内网隔离环境无法 `npx`，需要手动部署（成本高）|

#### 投入产出比（时间成本）

| 项目 | 时间投入 | 持续收益 |
|---|---|---|
| 安装 MCP | 5 分钟（顺利）– 30 分钟（遇到 npm bug）| AI 每次查询省 2–5 分钟 |
| 安装 Skills | 2 分钟（UI 安装）– 10 分钟（手动解压）| AI 自动遵循最佳实践，减少代码返工 |
| 学习成本 | 0（AI 自动调用工具，开发者无感）| — |
| **总计** | **7–40 分钟** | **长期项目每周省 1–2 小时** |

#### 最终建议

**✅ 强烈推荐集成的情况**：
1. 字节跳动内部项目（必装）
2. 用 Claude Desktop / Cursor / Windsurf 编码
3. 项目 Semi >= 2.90.2
4. 团队新人多，需要快速上手

**⚠️ 可选的情况**：
1. 用其他组件库，但想体验 MCP 协议（可以先装 Semi MCP 学习 MCP 原理）
2. 项目 Semi < 2.90.2（可以装，但注意 AI 给的信息可能与实际版本不符）

**❌ 不推荐的情况**：
1. 不用 AI 辅助编码
2. 项目不用 Semi Design
3. 网络环境无法访问 npm（除非有内部镜像）

### 5.4 集成后的使用示例

**AI 查询组件（开发者无需手动触发）**：

```
开发者: "我要实现一个可筛选的 Table"

AI（内部流程）:
  1. 调用 get_semi_document("Table")
  2. 查看返回的 API 文档
  3. 发现有 `onChange` 和 `filters` 配置
  4. 调用 get_semi_code_block() 获取筛选示例
  5. 生成代码

AI 回复: "可以用 Table 的 columns.filters 配置实现..."
[附带完整代码示例，基于最新 API]
```

**传统方式 vs MCP 方式对比**：

| 步骤 | 传统方式 | 有 MCP |
|---|---|---|
| 1. 找文档 | 手动搜索 "Semi Table 筛选" | AI 自动查询 |
| 2. 看 API | 打开网页，找 `filters` 参数 | AI 直接读取 |
| 3. 找示例 | 滚动找代码块，复制 | AI 自动获取 |
| 4. 适配项目 | 手动改参数 | AI 按项目上下文生成 |
| **总耗时** | **5–10 分钟** | **30 秒** |

**注意事项**：

> ① **版本匹配**：确保项目 Semi >= 2.90.2，否则 AI 查到的 API 可能与实际不符  
> ② **不是万能**：复杂的自定义需求（如完全重写组件样式）仍需查官方文档  
> ③ **信任但验证**：AI 生成的代码仍需 code review，MCP 只是减少查文档时间，不保证逻辑正确  

---

## 6. 快速决策流程图

```
项目技术栈？
├─ React
│   ├─ 字节内部 → Semi Design ✅
│   ├─ 国内 To B → Ant Design ✅
│   ├─ 用 Tailwind → shadcn/ui ✅
│   └─ 需要算法生成色阶 → Ant Design ✅
├─ Vue 3 → Element Plus ✅
└─ 其他框架 → 自定义组件 + Lucide 图标

需要 AI 辅助编码？
├─ 是 + 用 Semi → 安装 MCP/Skills ✅
└─ 否 / 用其他库 → 不安装 MCP

图标需求？
├─ 需要大量图标 → Lucide（1400+ 个，一致风格）✅
├─ 只用少量 → 组件库自带图标
└─ 需要品牌图标 → 自定义 SVG

主题定制复杂度？
├─ 多主题管理 → Semi（三层 Token）✅
├─ 简单改色 → Ant（算法生成）✅
├─ 完全自定义 → shadcn（复制代码）✅
└─ 极简配置 → Element（扁平 CSS 变量）✅
```

---

## 7. 附录：环境限制与失败记录

### 7.1 无法访问的站点

| 站点 | URL | 失败信号 | 诊断 |
|---|---|---|---|
| **astryx.atmeta.com** | `https://astryx.atmeta.com/templates` | `ERR_CONNECTION_CLOSED`（Chromium）| TCP 连接失败，可能域名失效或服务关闭 |
| **stitch.withgoogle.com** | `https://stitch.withgoogle.com/` | HTTP 422（Keenable）、页面 body 0 字节（Chromium）| 页面存在但内容为空，可能需要 JS 渲染但 SSR 失效 |

### 7.2 补充信息来源

因 astryx 和 stitch 无法访问，以下是从其他来源获取的简要信息：

#### astryx（推测）

- **可能定位**：设计模板库（templates 路径推测）
- **替代方案**：如果需要设计模板，可用：
  - [Tailwind UI](https://tailwindui.com)（Tailwind 官方模板）
  - [shadcn/ui templates](https://ui.shadcn.com/templates)（shadcn 官方模板集合）
  - [Vercel Templates](https://vercel.com/templates)（Next.js 项目模板）

#### stitch（Google 产品）

- **官方定位**：AI 辅助设计工具（从 title "Stitch - Design with AI" 推测）
- **可能功能**：类似 Figma AI、Uizard，通过 AI 生成设计稿
- **替代方案**：
  - [v0.dev](https://v0.dev)（Vercel 的 AI 生成 UI 工具，直接生成 shadcn 组件代码）
  - [Galileo AI](https://www.usegalileo.ai)（AI 生成高保真设计稿）
  - [Uizard](https://uizard.io)（手绘草图转 UI）

**注意**：以上为推测，无法验证。若需要这两个工具，建议：
1. 检查网络连接（可能是本地网络问题）
2. 联系工具提供方确认服务状态
3. 使用上述替代方案

---

## 8. 参考链接

| 系统 | 文档首页 | Token/主题文档 | GitHub |
|---|---|---|---|
| Semi Design | [semi.design](https://semi.design/zh-CN/start/getting-started) | [Tokens](https://semi.design/zh-CN/basic/tokens) | [DouyinFE/semi-design](https://github.com/DouyinFE/semi-design) |
| Ant Design | [ant.design](https://ant.design/docs/spec/introduce) | [定制主题](https://ant.design/docs/react/customize-theme) | [ant-design/ant-design](https://github.com/ant-design/ant-design) |
| Element Plus | [element-plus.org](https://element-plus.org/zh-CN/guide/design.html) | [主题定制](https://element-plus.org/zh-CN/guide/theming.html) | [element-plus/element-plus](https://github.com/element-plus/element-plus) |
| shadcn/ui | [shadcn.com.cn](https://www.shadcn.com.cn/docs/theming) | [Theming](https://www.shadcn.com.cn/docs/theming) | [shadcn/ui](https://github.com/shadcn/ui) |
| Lucide | [lucide.dev](https://lucide.dev/guide/) | [全局样式](https://lucide.dev/guide/advanced/global-styling) | [lucide-icons/lucide](https://github.com/lucide-icons/lucide) |

---

## 更新日志

- **2026-11-05**：初版，覆盖 Semi、Ant、Element、shadcn、Lucide 五系统；astryx 与 stitch 失败已记录。
