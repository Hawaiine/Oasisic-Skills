# Shadowing 与实际加载验证

本文件回答两个问题：**同名 Skill 谁生效**，以及**怎么证明「真的加载了」**。

---

## 1. 三层状态必须分开取证

```
Discovered  ── 本机能发现它（目录扫描 / 索引 / 列表）
Registered  ── 本机把它登记为可用（安装记录 / hub 状态 / external 登记）
Loaded      ── Agent runtime 真实构建索引并命中，且内容与 linked files 实际可读
```

常见的危险组合：

| 组合 | 含义 | 判定 |
|------|------|------|
| discovered=yes, loaded=no | 只是看见，运行时不生效 | 未完成 |
| external dir 存在 + 同名 local 存在 | 可能被覆盖 | 先解决 shadowing |
| 列表里有名字 | 只证明登记/索引，不证明内容来自 canonical | 需 inspect + 内容比对 |
| 文件已就位 | 只是文件系统状态 | 需实际加载取证 |

**不要**用「目录存在」「列表里有」当作接入成功。

## 2. 层级优先级

Hermes 的 Skill 发现通常分成多档，例如（以**本机实际实现**为准）：

```
local（profile skills 目录）
project-local（受信任的项目目录）
external（skills.external_dirs）
hub-installed
builtin
```

必须做：

1. 读本机实现的优先级与冲突规则（源码/文档标注可能不一致，**以实际实现为准**）；
2. 找出同一 `name` 的**全部副本**，包含 archive / retired 目录，并标注是否为 active 发现路径；
3. 判断最终生效的是哪一份；
4. 确认生效版本就是 canonical source；
5. 确认旧 local copy **不会静默覆盖** canonical。

判定结果三选一：

```
NO SHADOW     —— 只有一个 active 副本，或生效项就是 canonical
LOCAL SHADOW  —— 旧 local 副本优先，canonical 被压住（必须处理）
STALE / OTHER —— 生效项是过期副本或临时工作目录
```

## 3. 实际加载的取证方式

至少完成 discover → inspect → **actual load** 三步，并留下可复现证据：

1. **Agent runtime 索引**
   走本机的 prompt / 索引构建路径（例如构建技能索引的函数），确认索引里**包含**该 Skill，
   并记录其描述行；同时确认旧 Skill 名字**已不在**索引中（退役后）。
2. **Skill 查看 / 检查**
   以名称解析该 Skill，确认：
   - 返回的 source 路径指向 **canonical checkout / canonical 安装位置**；
   - 返回的正文与 canonical 文件一致（版本号、章节、关键不变量）；
   - 声明了 linked files（references 等）且列表与仓库一致。
3. **Linked files 逐个可读**
   references / scripts / 资产逐个打开或读取字节数，确认不是空文件、不是 404。

补充判据（可选，但很有用）：

- 版本字段与 canonical 元数据一致；
- 用旧 Skill 名字调用解析应**失败**（证明退役生效）；
- 若本机有 CLI 检查命令，记录其输出与**已知覆盖范围**（见下）。

## 4. 按版本的能力差异（不要假设）

CLI 子命令的**覆盖范围**在不同版本会变化，例如可能出现：

- 某些列表命令只覆盖 local / builtin / hub，**不含 external dirs**；
- 某些 inspect 命令只检索远端 source，**不检索 external dirs**；
- 某些 URL 形式的 identifier 只在安装路径支持，检查路径不支持。

因此：

- 「列表里没有」≠「未接入」；
- 「列表里有」≠「加载的是 canonical」；
- 判断标准必须落在**索引构建 + 名称解析取到 canonical 内容 + linked files 可读**上。

> Historical Example（仅用于识别模式，勿当作当前事实）：
> 曾观测到「tap 已注册且 library 层可读，但 CLI 的 search / inspect 解析不到」、
> 「直接 URL 安装被按私网地址拦截」、「列表命令不覆盖 external dirs」三种组合同时出现。
> 正确处置是改用官方支持的 external dirs 并记录本机限制，而不是修改 Skill 仓库结构。

## 5. 运行时新鲜度（容易误判）

```
filesystem / config state changed   ≠   运行中进程已加载新 Skill
```

三层分别确认：

| 层 | 取证方式 | 说明 |
|----|----------|------|
| 文件/配置层 | 读文件、读配置、解析 YAML | 证明「装上了」 |
| 新进程层 | 新启动的进程执行检查命令 / 索引构建 | 证明「新进程能加载」 |
| 运行中进程层 | 当前服务的实际索引 / 实际调用 | 证明「现在生效」 |

需要刷新时优先选择：**重建 prompt / 新会话 / 新起进程**。
不要为验证而无必要地重启生产服务；如果必须重启，先说明影响。

## 6. 验证记录模板

```
Discovery:        PASS / FAIL   （依据：…）
Inspection:       PASS / FAIL   （返回 source：…；版本：…）
Actual loading:   PASS / FAIL   （依据：索引命中 + 名称解析 + 内容比对）
References:       X/Y           （逐个文件可读）
Same-name shadowing: NONE / LOCAL SHADOW / STALE
Runtime refresh:  REQUIRED / NOT REQUIRED（状态：文件层 / 新进程 / 运行中进程）
```
