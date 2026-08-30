# 🏗️ OpenWrt CI Skill

> OpenWrt 固件构建 CI/CD 最佳实践 —— 从 [Oasisic OpenWrt](https://github.com/Hawaiine/oasisic-openwrt) 实战提炼

[![build](https://github.com/Hawaiine/oasisic-openwrt/actions/workflows/openwrt-auto-build.yml/badge.svg)](https://github.com/Hawaiine/oasisic-openwrt/actions/workflows/openwrt-auto-build.yml)
[![OpenWrt](https://img.shields.io/github/v/release/openwrt/openwrt?logo=openwrt&label=OpenWrt&color=00b4ff)](https://openwrt.org)
[![Nikki](https://img.shields.io/github/v/release/nikkinikki-org/OpenWrt-nikki?logo=go&label=Nikki&color=ff6600)](https://github.com/nikkinikki-org/OpenWrt-nikki)

这是一个 **skill 文档 + 可复用模板** 仓库：给 Agent / 人类在搭建或维护 OpenWrt 固件 CI 时用，**不是**独立可编译的固件工程。

---

## 内容地图

| 路径 | 说明 |
|------|------|
| [`SKILL.md`](./SKILL.md) | 主 skill：流水线、feeds 语法、去重、Release、向导、陷阱、验收 |
| [`references/feeds-version-tracking.md`](./references/feeds-version-tracking.md) | `;` vs `^`、pin SHA、last_build、失败/成功 run 锚点 |
| [`templates/`](./templates/) | 从 oasisic-openwrt 同步的可工作模板（workflow / scripts / 向导片段） |

---

## 现行流水线（与 oasisic-openwrt 对齐）

```
check-upstream → build → qemu-smoke-test → release → persist-last-build
```

| 能力 | 现状 |
|------|------|
| 定时 | UTC 06:00 / 北京 14:00 检测上游 |
| 手动 | `force_build` + `nikki_ref`（Tag / 分支 / 短或完整 SHA） |
| Nikki 默认 | 最新 Release Tag |
| feeds 钉 Commit | **`url^完整40位SHA`**（禁止 `url;SHA`） |
| composite | `${OWRT_TAG}_nikki-${NIKKI_SHA}` |
| Release 标签 | `oasisic-{ver}-nikki-{shortsha7}` |
| 签名 | minisign → `sha256sums.minisig` 进 Release |
| 去重 | `persist-last-build` 回写 `last_build_version`（`[skip ci]`） |

**P0 教训：** check-upstream 绿 ≠ feeds 对。把完整 SHA 写成 `;SHA` 会在「配置 feeds」失败（run `30098510806`）。改 `^SHA` 后 pin 构建可全绿（run `30107519212`）。

---

## 怎么用

1. 读 `SKILL.md`（先 Pitfalls + feeds 表，再流水线细节）  
2. 拷贝 `templates/` 到你的固件仓库并改名/裁剪  
3. 配置 Secrets：`DISCORD_BOT_TOKEN`、`MINISIGN_*`  
4. 验收：

```bash
bash scripts/gen-feeds-conf.sh v25.12.5 <full40sha> | tail -1   # 必须含 ^
bash scripts/gen-feeds-conf.sh v25.12.5 v1.26.1 | tail -1       # 必须含 ;
```

5. 手动验证某 Nikki commit：Actions → Run workflow → `force_build=true`，`nikki_ref=<sha|main>`

---

## 参考实现

- 工程仓库：https://github.com/Hawaiine/oasisic-openwrt  
- 文档与 Release **以该仓库当前 `main` / Releases 为准**（可能清空重建，勿死链旧 tag）  
- 关键修复提交示例：`75a011b`（feeds `^SHA`）、`a4efa24`（dispatch + persist + 短 Release）

---

## 版本

| Skill 版本 | 说明 |
|------------|------|
| **2.0.0** | 对齐五阶段流水线、OpenWrt `;`/`^` 语法、pin SHA、去重回写、短 Release；模板从实仓同步；去掉过时 4 阶段/旧 Release 死链 |

---

## 许可证

[MIT](../../LICENSE)
