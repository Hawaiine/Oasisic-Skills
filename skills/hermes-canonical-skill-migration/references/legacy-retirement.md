# Legacy Skill 退役

本文件定义：什么时候**可以**退役旧 Skill、退役怎么做才可回滚、以及「残留」该怎么判。

核心原则：

```
先证明 canonical 可用，再退役旧入口。
退役 = 移出 active 发现路径，不是删除。
```

---

## 1. 先做 Capability Inventory（能力盘点）

对每个旧 Skill 逐项记录，**不看名字看能力**：

```
Skill:                    <name>
Purpose:                  它解决什么问题
Unique Knowledge:         独有的规则/事实（哪些在别处没有）
Operational Procedures:   可执行步骤（命令、顺序、分支条件）
Validation Gates:         它要求跑什么校验、什么算通过
Failure Modes:            它记录过的坑与症状
Historical Caveats:       只对历史情境成立的内容
Destination:              这些能力最终进入 canonical 的哪个位置（章节 / references 文件 / 明确废弃）
```

盘点完成的标准：**每个旧 Skill 的每一项能力都有一个明确去向**，没有「未归类」条目。

## 2. 合并判断：看领域，不看名字

多个旧 Skill 是否应收敛为 `one canonical Skill + references/`，判据是：

```
同一维护领域？  且  存在重复规范风险（两处描述同一规则 → 必然漂移）？
```

- 满足 → 收敛为**一个 canonical Skill**，专项流程落到 `references/`；
- 不满足 → 不要强行合并；不同领域各自保持独立 canonical。

**不要**规定「所有 Skill 都必须合并」，也不要仅凭名字相似就合并。

## 3. 退役门（Retirement Gate）

只有全部成立才允许把旧 Skill 移出 active 路径：

```
[ ] canonical source 已确定/已合并（进入默认分支或权威位置）
[ ] 本机 canonical checkout 与 canonical revision 一致且 clean
[ ] canonical Skill 可被发现
[ ] canonical Skill 实际可加载（不只是登记）
[ ] canonical 身份一致（目录名 == 入口 frontmatter.name == 元数据 name）
[ ] references 等 linked files 实际可读
[ ] 同名 shadowing 已解决（生效项就是 canonical）
[ ] 旧 Skill 能力已全部盘点并有去向
[ ] backup 已校验（文件数 + 摘要一致）
```

任一项不成立 → 不退役，报告缺失项。

## 4. 退役流程（可回滚）

```
ACTIVE  ──移到──▶  RETIRED  ──（必要时）──▶  ARCHIVED
```

而不是：

```
ACTIVE  ──▶  DELETED      ❌
```

要求：

1. 移出**活动发现路径**（保持在磁盘上，放到明确的 retired/归档目录）；
2. 保留并生成**迁移记录**：退役时间、原因、来源路径、目标路径、能力去向、canonical source；
3. 保留**备份**（含 manifest + 每个文件的摘要），并在退役后重新校验一次；
4. 写清单（manifest）时记录每个文件的 sha256，便于日后回滚验证；
5. 移走后复查：活动路径下同名 Skill 计数 = 0；canonical 仍在索引中。

顺序建议：**先退役最明确被完全吸收的那个**（例如其内容已整体并入 canonical 的某节/某 reference），
再处理其余；每退一个就复查一次索引。

## 5. 回滚路径

```
canonical 加载失败
        ↓
从 RETIRED / BACKUP 恢复旧 Skill 到活动路径（临时）
        ↓
排查并修复 canonical 接入
        ↓
重新退役（恢复必须在修复后回收，避免形成第二份长期源）
```

回滚是**临时手段**：不允许把恢复出来的副本长期留在活动路径里冒充 canonical。

## 6. 残留判定（不要用 grep=0）

退役后搜索旧名字一定会有命中，**不要**把 `grep = 0` 当唯一标准。逐条分类：

| 类别 | 说明 | 允许存在 |
|------|------|----------|
| ACTIVE | 仍在活动发现路径 | ❌（必须为 0，除非它就是要保留的 canonical） |
| CANONICAL | 当前 canonical 命中（例如 migration 记录里的说明） | ✅ |
| RETIRED | 退役目录里的副本 | ✅ |
| ARCHIVE | 更深的归档/历史目录 | ✅ |
| HISTORICAL | 历史文档中的记录 | ✅ |
| MIGRATION | 迁移表/迁移记录 | ✅ |
| FALSE-POSITIVE | 同名但无关（其它项目的相似命名） | ✅ |

最终硬标准：

```
active obsolete source = 0
active canonical source = 1
```

报告要给出**分类后的计数**，而不是一个 `grep` 数字。

## 7. 报告模板

```
Old Skills:
  <name>:
    Capabilities accounted: YES/NO
    Destination:            <canonical 章节 / references 文件 / 明确废弃>
    Retired:                YES/NO（路径：active → retired）
    Backup verified:        YES/NO（文件数 / 摘要）
Active canonical copies:  1
Active obsolete copies:   0
```

任何一项不能证明 → 不得宣布退役完成。
