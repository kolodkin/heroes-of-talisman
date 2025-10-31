# Playwright Configuration

## Environment Variables

### `PLAYWRIGHT_CHROMIUM_ARGS`

Comma-separated list of Chromium launch arguments to use during tests.

**Default**: Empty (uses Chromium defaults, no custom args)

**When to set**:

- Running tests in containerized environments (Docker, Claude Code, etc.)
- Chromium crashes with default configuration
- Restricted system environments with limited process spawning

**How to set**:

```bash
# In .env file
PLAYWRIGHT_CHROMIUM_ARGS=--single-process,--no-zygote,--disable-gpu

# Or via environment
export PLAYWRIGHT_CHROMIUM_ARGS="--single-process,--no-zygote,--disable-gpu"
npm run e2e
```

**Automatically set by**:

- `scripts/setup_cai_code` - Sets containerized environment flags for Claude Code

**Performance Note**:

- Custom args (especially `--single-process`) are **slower** than Chromium defaults
- Only set when necessary for stability
- Normal development machines should leave empty (default)

## Recommended Chromium Flags for Containerized Environments

When `PLAYWRIGHT_CHROMIUM_ARGS` is needed (e.g., in Claude Code), use these flags:

```bash
--single-process,--no-zygote,--disable-gpu,--disable-dev-shm-usage,--disable-setuid-sandbox,--no-sandbox,--disable-web-security,--disable-features=IsolateOrigins,site-per-process,--disable-blink-features=AutomationControlled,--disable-software-rasterizer
```

**Flag explanations**:

- `--single-process` - Run Chromium in single-process mode (prevents crashes in containers)
- `--no-zygote` - Disable zygote process spawning
- `--disable-gpu` - Disable GPU hardware acceleration
- `--disable-dev-shm-usage` - Don't use /dev/shm shared memory
- `--disable-setuid-sandbox` - Disable setuid sandbox
- `--no-sandbox` - Disable sandboxing
- `--disable-web-security` - Disable web security features
- `--disable-features=IsolateOrigins,site-per-process` - Disable site isolation
- `--disable-blink-features=AutomationControlled` - Hide automation detection
- `--disable-software-rasterizer` - Disable software rasterizer
