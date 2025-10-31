# Playwright Configuration

## Environment Variables

### `PLAYWRIGHT_SINGLE_PROCESS`

Controls whether Chromium runs in single-process mode during tests.

**Default**: `false`

**When to set to `true`**:

- Running tests in containerized environments (Docker, Claude Code, etc.)
- Chromium crashes with multi-process mode
- Restricted system environments with limited process spawning

**How to set**:

```bash
# In .env file
PLAYWRIGHT_SINGLE_PROCESS=true

# Or via environment
export PLAYWRIGHT_SINGLE_PROCESS=true
npm run e2e
```

**Automatically set by**:

- `scripts/setup_cai_code` - Sets to `true` for Claude Code environments

**Performance Note**:

- Single-process mode is **slower** than multi-process mode
- Only enable when necessary for stability
- Normal development machines should use `false` (default)

## Chromium Flags

The Playwright configuration applies different Chromium flags based on the environment:

**Always Applied** (stability flags):

- `--disable-gpu`
- `--disable-dev-shm-usage`
- `--disable-setuid-sandbox`
- `--no-sandbox`
- `--disable-web-security`
- `--disable-features=IsolateOrigins,site-per-process`
- `--disable-blink-features=AutomationControlled`
- `--disable-software-rasterizer`

**Conditionally Applied** (when `PLAYWRIGHT_SINGLE_PROCESS=true`):

- `--single-process` - Run Chromium in single-process mode
- `--no-zygote` - Disable zygote process spawning
