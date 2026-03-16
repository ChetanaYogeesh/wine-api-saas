# Session Log: Wine API SaaS Test Fixes

**Date:** March 16, 2026  
**Goal:** Fix failing tests and update CI pipeline

---

## Starting Context (from prior session summary)

- Prior work completed Phase 6: Webhooks, Analytics, Teams, White-label features
- All documentation updated
- Ruff lint errors fixed (22 → 0)
- App running in Docker (API on port 8000, PostgreSQL on 5432, Redis on 6379)
- Pushed to GitHub with CI/CD

**Problem:** 15 tests failing due to missing test database `wineapi_test`

---

## Investigation

### Initial State
- 18 tests collected
- 15 tests failing, 3 passing
- Error: `database "wineapi_test" does not exist`

### Files Examined
- `tests/conftest.py` - Original test configuration
- `tests/test_api.py` - Test cases
- `app/main.py` - FastAPI application
- `app/database.py` - Database configuration
- `.github/workflows/ci-cd.yml` - CI pipeline

---

## Solutions Attempted

### Attempt 1: SQLite for Testing
Updated `conftest.py` to use SQLite in-memory database instead of requiring PostgreSQL.

**Challenge:** The app's middleware (`track_usage`) uses `SessionLocal` directly, not the dependency injection. This caused the app to still try connecting to PostgreSQL.

**Solution:** Set `DATABASE_URL` environment variable in a session-scoped autouse fixture before any app imports.

### Attempt 2: FastAPI Dependency Overrides
Tried using `app.dependency_overrides[get_db]` to inject test database.

**Issue:** This only works for route handlers using `Depends(get_db)`, not for middleware that directly imports `SessionLocal`.

### Attempt 3: Set Environment Variable Before Import (SUCCESS)
Created an autouse session fixture that sets `DATABASE_URL` to SQLite before any app modules are imported:

```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DATABASE_URL"] = f"sqlite:///{path}"
    yield
    # cleanup
```

This ensured the entire app (including middleware) uses SQLite during tests.

---

## Additional Fixes

### Fix 1: Lint Errors
Removed unused imports flagged by ruff:
- `pytest` import in test_api.py
- Various unused imports in conftest.py

### Fix 2: CI Pipeline Update
Removed PostgreSQL and Redis services from CI - tests now use SQLite.

### Fix 3: Node.js Deprecation Warnings
Updated workflow to opt into Node.js 24:
```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
```

### Fix 4: Duplicate env Section
Merged two `env` sections into one to fix validation error.

---

## Final State

- **18 tests passing**
- **0 lint errors**
- **CI pipeline updated** with Node.js 24 support

---

## Commits Made

| Commit | Message |
|--------|---------|
| 4322128 | Fix test database configuration - use SQLite for testing |
| 62d8f2b | CI: Add test database creation step |
| a477d45 | Fix tests: use SQLite in-memory database, update CI |
| 5cc65a5 | Fix: set DATABASE_URL before importing app modules |
| 31a083c | CI: Fix Node.js deprecation warnings |
| 8927cc3 | CI: Fix Node.js deprecation by setting env var globally |
| a3ff1c3 | CI: Merge env sections into one |

---

## Key Learnings

1. **Test Database Injection:** When testing FastAPI apps with middleware that uses database connections directly, setting environment variables before module import is more reliable than dependency overrides.

2. **CI Pipeline:** SQLite is sufficient for testing - no need for PostgreSQL/Redis services unless testing specific backend features.

3. **GitHub Actions:** The `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` env var must be set at the workflow level (not per-job) to affect all actions.

---

## Files Modified

- `tests/conftest.py` - Complete rewrite for SQLite testing
- `tests/test_api.py` - Removed unused pytest import
- `.github/workflows/ci-cd.yml` - Removed DB services, added Node.js 24 opt-in
