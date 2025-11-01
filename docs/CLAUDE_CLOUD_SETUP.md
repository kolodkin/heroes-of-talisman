# Claude Cloud / Containerized Environment Setup

This guide documents the setup process for running tests in Claude Cloud or similar containerized environments where you don't have Docker available.

## Quick Start

```bash
# One-command setup
./scripts/setup_claude_cloud

# Run tests
uv run pytest -v                 # Backend tests
CI=true npm run e2e              # E2E tests
```

## Requirements

The following must be pre-installed:

- PostgreSQL 16 (system package)
- Redis (system package)
- Python 3.12
- Node.js (LTS)
- uv (Python package manager)
- Playwright with Chromium

## What the Setup Script Does

### 1. PostgreSQL Configuration

**Problem**: PostgreSQL SSL certificates have incorrect permissions in containerized environments.

**Solution**: Disable SSL for local development:

```bash
# /etc/postgresql/16/main/postgresql.conf
ssl = off
```

### 2. Authentication Setup

**Problem**: Default PostgreSQL authentication requires passwords that may not be set.

**Solution**: Use trust authentication for localhost (testing only!):

```bash
# /etc/postgresql/16/main/pg_hba.conf
host    all    all    127.0.0.1/32    trust
```

⚠️ **Warning**: Trust authentication is insecure. Only use in isolated test environments.

### 3. File Ownership

**Problem**: PostgreSQL config files may have wrong ownership if PostgreSQL runs as non-postgres user.

**Solution**: Adjust ownership to match the PostgreSQL process user:

```bash
chown claude:claude /etc/postgresql/16/main/*.conf
```

### 4. Service Management

Start and verify PostgreSQL and Redis:

```bash
# Start PostgreSQL
pg_ctlcluster 16 main start

# Start Redis
redis-server --daemonize yes

# Verify
pg_isready -h localhost -p 5432
redis-cli ping
```

## Playwright Configuration for Containers

When running as root in containers, Chromium requires special flags to bypass sandboxing restrictions.

### Environment Variable Configuration

Browser arguments are configured via the `PLAYWRIGHT_BROWSER_ARGS` environment variable in `.env`.

**Automatic Configuration**: The `./scripts/setup_claude_cloud` script automatically sets container-specific browser args:

```bash
# Automatically set by setup_claude_cloud
PLAYWRIGHT_BROWSER_ARGS=--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage,--disable-gpu,--disable-software-rasterizer,--disable-extensions,--single-process
```

**Default Behavior**: By default (via `./scripts/setup --no-docker`), `PLAYWRIGHT_BROWSER_ARGS` is empty, which uses minimal default flags:

```bash
# Default from create_env.sh for local/CI environments
PLAYWRIGHT_BROWSER_ARGS=
```

The args are comma-separated chromium flags. The config is automatically loaded by `playwright.config.js`:

```javascript
const getBrowserArgs = () => {
  if (process.env.PLAYWRIGHT_BROWSER_ARGS) {
    return process.env.PLAYWRIGHT_BROWSER_ARGS.split(",")
      .map((arg) => arg.trim())
      .filter(Boolean);
  }
  // Default args for local development (minimal sandboxing issues)
  return ["--no-sandbox", "--disable-setuid-sandbox"];
};

const browserArgs = getBrowserArgs();
```

### Browser Args Explained

- `--no-sandbox` - Required for root user
- `--disable-setuid-sandbox` - Required for root user
- `--single-process` - **Critical**: Prevents crashes in containers
- `--disable-dev-shm-usage` - Avoid /dev/shm issues
- `--disable-gpu` - Software rendering
- `--disable-software-rasterizer` - Disable GPU rasterization
- `--disable-extensions` - No browser extensions

**Critical Flag**: `--single-process` prevents Chromium crashes in containerized environments.

### Customizing Browser Args

To use different browser args, modify `PLAYWRIGHT_BROWSER_ARGS` in `.env`:

```bash
# Empty (default for local/CI - uses minimal defaults from playwright.config.js)
PLAYWRIGHT_BROWSER_ARGS=

# Minimal (if you need basic sandboxing disabled)
PLAYWRIGHT_BROWSER_ARGS=--no-sandbox,--disable-setuid-sandbox

# Full containerized support (automatically set by setup_claude_cloud)
PLAYWRIGHT_BROWSER_ARGS=--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage,--disable-gpu,--disable-software-rasterizer,--disable-extensions,--single-process
```

**When to use each**:

- **Empty** - Local development machines and well-configured CI/CD
- **Minimal** - When running as root but not in containers
- **Full** - Claude Cloud and containerized environments (auto-set by setup_claude_cloud)

## Running Tests

### Backend Tests

Backend tests are stable and don't require special configuration:

```bash
uv run pytest -v
# Expected: 131/131 tests pass
```

### E2E Tests

E2E tests benefit from retry logic in containerized environments:

```bash
# With retries (recommended)
CI=true npm run e2e

# Without retries (may be flaky)
npm run e2e
```

**Expected Results**:

- With `CI=true`: All 17 tests pass (marked as "flaky" if retries needed)
- Without `CI=true`: 11-12 tests pass, 5-6 may fail due to timing

## Known Issues

### Test Flakiness

E2E tests may be flaky due to:

1. **Race Condition in Test Cleanup**
   - Tests delete games at startup while WebSocket connections are still open
   - Server throws "Game not found" and crashes handling the error
   - **Impact**: First run of test may fail, retry succeeds
   - **Workaround**: Use `CI=true` to enable retries

2. **Service Instability**
   - PostgreSQL/Redis may crash during extended test runs
   - **Impact**: All tests fail until services restarted
   - **Workaround**: Monitor services, restart with `./scripts/setup_claude_cloud`

3. **API Error Parsing**
   - Test helper assumes all errors are JSON
   - Server sometimes returns plain text errors
   - **Impact**: Tests fail with "SyntaxError: Unexpected token 'I'"
   - **Status**: Application bug, not infrastructure issue

### Checking Service Health

```bash
# Quick health check
pg_isready -h localhost -p 5432 && redis-cli ping && echo "✓ All services healthy"

# If services are down
pg_ctlcluster 16 main start
redis-server --daemonize yes
```

## Differences from CI/CD

CI/CD environments typically have:

- Managed PostgreSQL/Redis services (don't crash)
- Better resource isolation
- Retries enabled by default
- No root user restrictions

This setup mimics CI/CD behavior in containerized environments.

## Troubleshooting

### PostgreSQL won't start

```bash
# Check logs
tail -50 /var/log/postgresql/postgresql-16-main.log

# Common issues:
# - SSL certificate permissions → Disable SSL
# - Config file ownership → Fix with chown
# - Port already in use → Kill existing process
```

### Chromium crashes immediately

```bash
# Verify Playwright config has --single-process flag
grep -A 10 "launchOptions" playwright.config.js

# Test manually
npx playwright test e2e/home.spec.js --headed
```

### All tests fail with "connection refused"

```bash
# Services crashed - restart them
./scripts/setup_claude_cloud

# Or manually:
pg_ctlcluster 16 main start
redis-server --daemonize yes
```

### Tests fail with database errors

```bash
# Re-run migrations
uv run alembic upgrade head
```

## Clean Restart

```bash
# Stop services
pg_ctlcluster 16 main stop
pkill redis-server

# Clear data (optional - will lose test data)
rm -rf /var/lib/postgresql/16/main/*

# Re-initialize (if cleared data)
pg_createcluster 16 main --start

# Run setup
./scripts/setup_claude_cloud
```

## Security Notes

⚠️ **These configurations are for testing only!**

- Trust authentication bypasses all password checks
- Running as root is insecure
- No SSL encryption on database connections
- Chromium sandboxing disabled

**Never use these configurations in production.**
