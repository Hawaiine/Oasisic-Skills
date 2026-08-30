# Agnes AI Custom Provider Reference

Single-key custom provider for Agnes AI (Sapiens AI) via apihub.agnes-ai.com.

## Config Shape

```yaml
custom_providers:
  - name: agnes
    base_url: https://apihub.agnes-ai.com/v1
    api_mode: chat_completions
    models:
      - id: agnes-2.0-flash
        name: Agnes-2.0-Flash
```

## .env

```bash
AGNES_API_KEY=<your-key>
```

Path: `$HERMES_HOME/.env` (typically `/opt/data/.env` or `~/.hermes/.env`)

## Env Var Convention

Auto-derived as `{NAME}_API_KEY` = `AGNES_API_KEY`. No `hermes auth add` or `credential_pool_strategies` needed — this is a single-key provider.

## Verified Model IDs (from /v1/models)

| Model ID | Display Name | Type |
|----------|-------------|------|
| `agnes-2.0-flash` | Agnes-2.0-Flash | Text + tool calls + vision |
| `agnes-1.5-flash` | Agnes-1.5-Flash | Text (previous gen) |
| `agnes-image-2.1-flash` | Agnes-Image-2.1-Flash | Image generation |
| `agnes-image-2.0-flash` | Agnes-Image-2.0-Flash | Image generation |
| `agnes-video-v2.0` | Agnes-Video-v2.0 | Video generation |

## Verification

After configuration, verify independently of Hermes routing:

```bash
# List models (confirms endpoint + key)
curl -s https://apihub.agnes-ai.com/v1/models \
  -H "Authorization: Bearer *** | python3 -m json.tool

# Test chat completions
curl -s https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer *** \
  -d '{"model":"Agnes-2.0-Flash","messages":[{"role":"user","content":"Hi"}],"max_tokens":10}'
```

The model ID in the API request is case-sensitive: `Agnes-2.0-Flash` (with capital A and F).

## Activation

To use Agnes as the active provider after adding the config:

```bash
hermes config set model.provider custom:agnes
hermes config set model.default agnes-2.0-flash
```

Then restart gateway (from an external terminal, not inside gateway):

```bash
hermes gateway restart          # if outside gateway
s6-svc -r /run/s6/services/main-hermes   # s6 deployments
```

Or `/reset` in CLI mode.

## Base URL

`https://apihub.agnes-ai.com/v1` — OpenAI-compatible `/v1/chat/completions` endpoint.

Docs: https://agnes-ai.com/zh-Hans/docs/cid2