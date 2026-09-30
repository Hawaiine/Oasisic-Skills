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
skills/hermes-config-expert/
├── README.md                          👈 本文件
├── SKILL.md                           👈 核心：配置专家 System Prompt（以文件实际内容为准）
├── meta.yaml                          👈 根 README 脚本读取的元数据
└── references/                        👈 典型 Provider 配置示例
    ├── sensenova-custom-provider.md   # 自定义 Provider + 多 Key 凭证池
    ├── agnes-ai-custom-provider.md    # 单 Key Provider + .env 自动发现
    ├── firecrawl-mcp-setup.md         # MCP Server 集成
    ├── model-speed-testing.md         # 模型延迟基准测试
    └── discord-home-channel.md        # Discord 默认投递频道
```

---

## 📋 核心规则

- 📖 新增或修改 Provider 前，先查 Hermes 官方文档和对应 Provider 官方资料；当前新增配置使用 `providers` 字典，旧 `custom_providers` 仅作迁移参考。
- 💾 任何涉及配置的修改前，必须同时备份 `config.yaml`、`auth.json`、`.env`，共享北京时间时间戳；每个文件只保留最近 3 份。
- 🔒 真实 API key、token、密码、Cookie、私钥、连接字符串和 `.env` 内容不得进入 Skill、README、commit、branch 或 PR。
- 🛡️ GitHub 推送或创建 PR 前，必须检查 diff 并完成脱敏扫描；发现疑似敏感信息立即停止。
- 🔄 GitHub 修改默认走分支 + PR，禁止直接推送 `main`，除非明确授权；提交信息必须是详细中文并带 emoji。
- ⬆️ Hermes 升级后查官方文档与 GitHub 仓库，核对 Release、Breaking Changes、新功能和配置迁移影响。

---

## 🚀 用法

### 作为 Hermes Skill 加载

将 `SKILL.md` 放入 Hermes skills 目录：

```bash
mkdir -p $HERMES_HOME/skills/hermes-config-expert
cp SKILL.md $HERMES_HOME/skills/hermes-config-expert/SKILL.md
```

之后 Hermes Agent 在涉及 Provider、Model、config.yaml 等配置相关任务时会自动加载此 skill。

### 作为配置手册

直接阅读 `SKILL.md` 获取完整工作流的每一步操作细节和命令。`references/` 目录下的文件是经过验证的第三方 Provider 配置示例和模式说明。

---

## 🧩 参考文件详解

### `references/sensenova-custom-provider.md`
**自定义 Provider + 多 Key 凭证池模式**

配置要点：
- 使用当前官方 `providers:` 字典；旧 `custom_providers:` 列表仍可运行，但不是新增配置的推荐格式
- 字段映射：`base_url → api`、`api_mode → transport`、`model → default_model`；模型 `id` 和显示名必须保留
- 凭证池使用 `custom:<name>` 作为 key
- `credential_pool_strategies` 使用 **裸名**（不带 `custom:` 前缀）—— 这是 Hermes 的设计不对称，不是错误

### `references/agnes-ai-custom-provider.md`
**单 Key Provider + `.env` 自动发现模式**

配置要点：
- 使用当前官方 `providers` 字典和 `key_env`；旧 `custom_providers` 仅用于迁移参考
- 环境变量名显式写为 `AGNES_API_KEY`
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
