# Sensenova Custom Provider Reference

Session-specific config details for the sensenova custom endpoint setup.

## Config Shape

```yaml
model:
  default: deepseek-v4-flash
  provider: custom:sensenova
  base_url: ''

custom_providers:
  - name: sensenova
    base_url: https://token.sensenova.cn/v1
    api_mode: chat_completions
    models:
      - id: deepseek-v4-flash
        name: deepseek-v4-flash
      - id: sensenova-6.7-flash-lite
        name: sensenova-6.7-flash-lite

credential_pool_strategies:
  custom:sensenova: round_robin
```

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
