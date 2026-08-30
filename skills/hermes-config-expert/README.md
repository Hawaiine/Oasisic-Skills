# Hermes 配置专家 🤖⚙️

> **一份严格、可验证、可回滚的 Hermes Agent 配置工作流规范。**
>
> 配置正确性永远高于执行速度。

---

## 📖 这是什么？

这是一个面向 [Hermes Agent](https://hermes-agent.nousresearch.com/) 的配置管理知识库。它的核心是一份 **配置专家系统提示（System Prompt）**，定义了从环境发现、官方文档验证、备份修改、逐项验证到回滚的完整闭环工作流。

此外还包含经过验证的第三方 Provider 配置参考，作为动手实践的例子。

---

## 📁 文件结构

```
hermes-config-expert/
├── README.md                          👈 本文件
├── SKILL.md                           👈 核心：配置专家 System Prompt（1737 行）
└── references/                        👈 典型 Provider 配置示例
    ├── sensenova-custom-provider.md   # 自定义 Provider + 多 Key 凭证池
    ├── agnes-ai-custom-provider.md    # 单 Key Provider + .env 自动发现
    ├── firecrawl-mcp-setup.md         # MCP Server 集成
    └── model-speed-testing.md         # 模型延迟基准测试
```

---

## 🎯 核心原则

| # | 原则 | 说明 |
|---|:---|:---|
| 🔍 | **官方文档优先** | 任何配置前必须查询最新版 Hermes 官方文档 + 第三方 Provider 官方文档 |
| 📋 | **环境自动发现** | 不假设路径，不写死配置。每次执行 `echo $HERMES_HOME` / `hermes profile` 确认 |
| 💾 | **备份先行** | 修改前 **三个文件（config.yaml / auth.json / .env）** 共用北京时间戳备份 |
| ⚡ | **CLI 优先** | 能用 CLI 绝不手动编辑。**例外**：`custom_providers` 禁止 CLI 写入（会序列化为字符串） |
| ✅ | **一步一验证** | 每次修改后立即：config check → YAML 校验 → JSON 校验 → API Probe → hermes model |
| 🔄 | **可回滚** | 验证失败立即回滚到最新备份，再次验证确认恢复 |
| 🧹 | **清理临时文件** | 验证全部通过后主动清理本次任务产生的临时脚本 |
| ✋ | **最小变更** | 只改达成目标的最小范围，无关配置不动 |
| 🔒 | **Key 安全** | 输出时 API Key 仅显式前 8 位 + **** + 末 4 位 |
| ⚠️ | **高风险确认** | 覆盖/删除/回滚操作前输出操作摘要，等待用户"确认" |

---

## 🚀 用法

### 作为 Hermes Skill 加载

将 `SKILL.md` 放入 Hermes skills 目录：

```bash
mkdir -p $HERMES_HOME/skills/hermes-configuration
cp SKILL.md $HERMES_HOME/skills/hermes-configuration/SKILL.md
```

之后 Hermes Agent 在涉及 Provider、Model、config.yaml 等配置相关任务时会自动加载此 skill。

### 作为配置手册

直接阅读 `SKILL.md` 获取完整工作流的每一步操作细节和命令。`references/` 目录下的文件是经过验证的第三方 Provider 配置示例和模式说明。

---

## 🧩 参考文件详解

### `references/sensenova-custom-provider.md`
**自定义 Provider + 多 Key 凭证池模式**

配置要点：
- `custom_providers` 手动编辑，禁止 CLI 写入
- 凭证池使用 `custom:<name>` 作为 key
- `credential_pool_strategies` 使用 **裸名**（不带 `custom:` 前缀）—— 这是 Hermes 的设计不对称，不是错误

### `references/agnes-ai-custom-provider.md`
**单 Key Provider + .env 自动发现模式**

配置要点：
- 环境变量名自动推导为 `{NAME}_API_KEY`（如 `AGNES_API_KEY`）
- 无需 `hermes auth add`，无需 `credential_pool_strategies`
- 适合只有一个 API Key 的场景，配置最简单

### `references/firecrawl-mcp-setup.md`
**MCP Server 集成模式**

配置要点：
- 通过 `hermes mcp add` 连接外部 MCP 服务，注入 26 个工具
- 凭证通过 `.env` 注入，config.yaml 引用 `${FIRECRAWL_API_KEY}`
- MCP 服务器需要新 session 才能生效（`/reset`）

### `references/model-speed-testing.md`
**跨 Provider 模型延迟对比**

配置要点：
- 测量 TTFT（首 token 延迟），使用 Python + curl 循环
- 先 warm-up 排除 DNS/TLS 连接影响
- 数据用于确定"哪个模型最快"，指导 provider 选择和 fallback 排序

---

## 🎮 适用场景

当你要执行以下任一操作时，加载这个 skill：

- 新增 / 切换 / 删除 Custom Provider
- 修改默认 Model 或 Fallback 链
- 添加 / 轮换 API Key
- 排查 Provider 不可见、401 / 404、请求打错地址等问题
- 在 Docker 多实例环境中修改配置并重启
- 同步更新消息平台的 Bot 指令菜单

---

## 🔐 安全说明

- 所有参考文件中的 API Key **已脱敏**为 `<your-key>` / `***` 占位符
- 真实的 `base_url` 和模型名称为 Provider 公开信息，非敏感数据
- 使用时请将占位符替换为你自己的凭据

---

## 🤝 贡献 & 定制

这套流程是根据实际配置 Hermes Agent 多个第三方 Provider 的过程中总结出来的。如果你想：

- **添加新的 Provider 示例** → 在 `references/` 下创建新文件
- **调整工作流规则** → 修改 `SKILL.md` 中的对应章节
- **补充故障排查经验** → 在常见错误速查表中新增行

---

## 📄 License

MIT — 自由使用、修改、分发。保持出处即可。

---

*Happy Hermes Configuring! 🎉*
