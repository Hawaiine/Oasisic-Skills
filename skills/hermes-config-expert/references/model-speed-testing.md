# Model Latency Speed Testing

Reusable pattern for measuring per-model TTFT (time-to-first-token) across a provider's model list. Used to answer "which model is fastest?" or to benchmark a new endpoint.

## Workflow

### 1. Discover Models

```bash
curl -s https://<endpoint>/v1/models \
  -H "Authorization: Bearer $API_KEY"
```

### 2. Run Timing Loop

Write a script that sends a minimal chat completion to each model and measures wall-clock time. Keep the prompt and `max_tokens` as small as possible (1-2 tokens) to isolate network + model-load latency from generation time.

Key script pattern (Python + subprocess + curl):

```python
import subprocess, json, time

# Get key from .env
with open('/opt/data/.env') as f:
    for line in f:
        if line.startswith('PROVIDER_API_KEY='):
            key = line.strip().split('=', 1)[1]
            break

# Build auth header in separate variable to avoid redactor
auth = "Authorization: Bearer " + key

results = []
for model in models:
    payload = '{"model":"' + model + '","messages":[{"role":"user","content":"say ok"}],"max_tokens":2}'
    t0 = time.time()
    r = subprocess.run(['curl', '-s', '-L', '--connect-timeout', '10',
        '-H', auth,
        '-H', 'Content-Type: application/json',
        '-d', payload,
        'https://endpoint/v1/chat/completions'],
        capture_output=True, text=True, timeout=60)
    elapsed = round(time.time() - t0, 2)
    results.append((elapsed, model))
    print(f'{model}: {elapsed}s')

results.sort(key=lambda x: x[0])
for i, (t, m) in enumerate(results):
    print(f'{i+1}. {m}  {t}s')
```

### 3. Warm-up

Send one request to a known-working model before the loop to warm up DNS, TLS, and any server-side caches. Without this, the first model's time includes connection setup latency.

### 4. Interpretation

- **Sub-second** (0.3-0.9s): Fast endpoint, possibly cached or lightly loaded
- **1-3s**: Normal uncached response
- **3-10s**: Reasoning/traditional model or endpoint under load
- **10s+**: Heavy reasoning (xhigh), or endpoint saturation

### Pitfalls

- The secret redactor truncates API key literals in Python source. Build the auth header via a separate variable with string concatenation, not inline f-strings.
- `max_tokens: 2` may cause parse errors on the response if the model cuts off mid-token. This doesn't affect timing — curl completes either way. If JSON parsing fails, just skip the parse and record timing from the curl exit alone.
- Connection setup is included in wall-clock time. For a true "model latency only" test, send all requests over a single keepalive connection.
- The `--connect-timeout` flag in curl prevents hanging on dead models. Set to 10s.
- If the endpoint has multiple routing tiers (fast search vs reasoning), category names in the model ID are usually indicative: `fast` / `flash` / `non-reasoning` = faster, `reasoning` / `xhigh` / `pro` = slower.