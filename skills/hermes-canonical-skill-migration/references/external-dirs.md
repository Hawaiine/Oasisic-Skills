# External Skill Directories

当官方 tap 与 direct URL install 都不可用时，Hermes 的 external skill directory 是**官方支持**的替代机制。
它的语义是：

```
external dir = Hermes 直接消费（只读）一个外部 canonical checkout
```

**不是**「安装一份本地副本」。本文件给出前置条件、配置纪律、只读性验证与 source inventory。

---

## 1. 前置条件（缺一不可）

```
[ ] 该目录是一个 Git checkout（不是复制目录 / 打包解压目录 / scratch 目录）
[ ] 位于仓库默认分支（main / master）
[ ] 工作区 clean
[ ] HEAD == origin/<default>（up to date）
[ ] 目录下的 Skill 结构符合 Hermes 规范
[ ] 本机 Hermes 实现支持 external dirs（读代码/配置 schema，不靠文档推断）
```

处理顺序（**只允许快进**）：

```
git fetch
↓
确认 working tree clean
↓
fast-forward 到 origin/<default>
```

**STOP 条件**：工作区 dirty、有未提交改动、有本地领先提交 —— 停止并报告，
不要 `reset --hard` / `clean -fd` / 强制同步 / 覆盖用户改动，除非用户明确授权。

## 2. 三类目录必须能分开

| 类型 | 特征 | 可否作为 external source |
|------|------|--------------------------|
| **canonical checkout** | 默认分支、clean、与远端一致、长期存在 | ✅ 唯一允许的 |
| **working copy** | 正在开发/建 PR 的分支，可能有脏文件 | ❌ |
| **temporary / scratch copy** | 缓存目录、打包解压、一次性克隆 | ❌ |
| **installed copy** | 由包管理器/安装器落地的副本 | 属于 consumer，不是 source |

同一台机器上出现多个同名 Skill 时，先建立 **Source Inventory**：

```
path | source type（canonical / working / temporary / installed）| branch+revision
     | active / inactive | canonical or not | shadowing status
```

## 3. 配置修改纪律

```
read → backup → minimal targeted edit → verify diff → runtime validation
```

- **先备份**：同一时间戳备份 `config.yaml`、`auth.json`、`.env`（存在即备份），各留独立副本。
- **最小精确改动**：优先单行/单键替换；**禁止**大段重写、整文件覆盖、重排。
- `.env` 不得被 truncate / clear / 重排；与本次无关的字段一律不动。
- 改后立即验证：
  - 文件仍可被解析；
  - 读回配置中该键的实际值符合预期；
  - 其它文件字节未变（可比对备份）；
  - 行数/结构变化与预期改动量一致。
- 启用 external dirs 之后，**不要马上删除旧 Skill**：先完成发现与加载验证。

配置示例（具体键名与层级以**本机版本 schema**为准）：

```yaml
skills:
  external_dirs:
    - <absolute-path-to-canonical-checkout>/skills
```

## 4. 只读性验证（必须以本机实现为准）

external dirs **不一定是文件系统层的只读边界**。必须检查本机实现里与写入相关的路径：

- Skill 管理/curation 流程是否会在该目录内写文件（创建、更新、删除）；
- sync / update 流程是否会把 external Skill 当作可改写对象；
- 名称冲突时是否会把 external 内容复制进本地目录。

判定与动作：

| 本机实现行为 | 结论 | 动作 |
|--------------|------|------|
| external 被标记为外部所有、curation 拒绝写入、sync 不覆盖 | 可安全使用 | 记录证据（文件/行号），继续迁移 |
| 存在写入路径，或无法确认 | **STOP** | 先做安全评估（文件系统权限 / 只读挂载 / 独立用户），否则不启用 |
| 名称冲突时 external 会被复制到本地 | 会产生第二份副本 | 先解决 shadowing，再评估是否仍适用 |

> 原则：`Git repository = canonical editable source`，`Hermes = read consumer`。
> 若本机无法保证 Hermes 不会改写 canonical checkout，则不应启用该目录作为 source。

## 5. 启用后的确认

```
[ ] 新进程能发现该 Skill
[ ] inspect / view 返回的 source 指向 canonical checkout
[ ] 返回内容与 canonical 文件一致
[ ] references 全部可读
[ ] 同名副本的生效顺序符合预期
[ ] canonical checkout 的工作区状态未因 Hermes 发生变化（验证后复查 git status）
```

## 6. 不要顺手清理

迁移完成后可能同时存在：tap 注册、stray hub、旧 clone、scratch copy、retired Skill、backup、分支。
它们**不等于**待删垃圾。先分类再谈清理：

```
ACTIVE / CANONICAL / RETIRED / STRAY / TEMPORARY / HISTORICAL
```

未经明确审计不执行 cleanup；尤其不要为了「看起来干净」而删除 tap 注册（可能仍被其它 consumer 使用）。
