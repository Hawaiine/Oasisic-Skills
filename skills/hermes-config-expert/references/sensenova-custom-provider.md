# Sensenova Custom Provider Reference

Session-specific config details for the sensenova custom endpoint setup.

## Config Shape（当前官方格式）

新增 Provider 前，先查 Hermes 官方文档和 Sensenova 官方文档。当前使用 `providers` 字典；旧 `custom_providers` 列表仅作迁移参考。

```yaml
providers:
  sensenova:
    api: https://token.sensenova.cn/v1
    transport: chat_completions
    default_model: deepseek-flash
    models:
      - id: deepseek-flash
        name: deepseek-flash
      - id: sensenova-6.8-flash-lite
        name: sensenova-6.8-flash-lite
      - id: deepseek-v4-pro
        name: deepseek-v4-pro
      - id: deepseek-v4-flash
        name: deepseek-v4-flash
      - id: glm-5.2
        name: glm-5.2
      - id: kimi-k3
        name: kimi-k3

credential_pool_strategies:
  sensenova: round_robin
```

API key 应放在 `.env` 或凭证池中，不要写入 YAML、README、Skill 或 git。

## Auth.json Pool Key

```
credential_pool["custom:sensenova"] = [
  { "auth_type": "api_key", "source": "manual", ... },
  ...
]
```

## CLI Commands Used

```bash
hermes auth add custom:sensenova --type api-key --api-key sk-...
hermes auth list custom:sensenova
hermes config set credential_pool_strategies '{}'
```

## Verified Model IDs

- `deepseek-v4-flash` — returns 200, normal chat completion response
- `sensenova-6.7-flash-lite` — listed in config, not yet probed

## Base URL

All requests go to: `https://token.sensenova.cn/v1`

Docs: https://platform.sensenova.cn/docs
