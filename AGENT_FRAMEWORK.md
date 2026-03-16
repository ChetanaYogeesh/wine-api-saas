# Wine API SaaS - Agent Framework Setup

This document describes how to convert the wine-api-saas project to use the agent harness framework similar to [everything-claude-code](https://github.com/affaan-m/everything-claude-code).

---

## What is the Agent Framework?

The agent framework is a **performance optimization system for AI agent harnesses** that provides:

- **Specialized agents** - Subagents for delegation (planner, code reviewer, security reviewer, etc.)
- **Skills** - Workflow definitions and domain knowledge
- **Slash commands** - Quick execution commands
- **Rules** - Always-follow coding guidelines
- **Hooks** - Trigger-based automations
- **Memory persistence** - Save/load context across sessions

---

## Original Wine API vs Agent Framework

| Aspect | Original Wine API (FastAPI App) | Agent Framework |
|--------|--------------------------------|-----------------|
| **What it is** | The actual REST API application | AI agent guidance/config |
| **Purpose** | Serves wine data to users | Helps AI agents build/maintain the API |
| **Runs in production?** | Yes (Docker container) | No (used during development) |
| **Files** | `app/main.py`, `app/data.py`, `tests/` | `AGENTS.md`, `skills/`, `commands/` |
| **Who uses it** | API consumers (curl, frontend) | Developers/AI agents |

### Simple Explanation

**Original Wine API:**
- The actual product that runs and serves data
- Handles HTTP requests, returns wine JSON
- What you deploy to production

**Agent Framework:**
- A "how-to guide" for AI agents
- Tells AI how to work on the project
- Contains skills, commands, rules
- Makes future development faster

### Analogy

| | |
|---|---|
| **Original API** | The car (what drives on the road) |
| **Agent Framework** | The owner's manual (tells you how to drive/maintain it) |

The agent framework doesn't change how the API works - it changes how **you/AI work on the code**.

---

## Project Structure with Agent Framework

```
wine-api-saas/
├── AGENTS.md                    # Agent definitions
├── CLAUDE.md                    # Project context for AI
├── skills/
│   ├── fastapi-patterns/       # FastAPI best practices
│   ├── wine-api-workflow/     # Wine API specific workflows
│   └── tdd-workflow/          # Test-driven development
├── commands/
│   ├── wine-stats.md          # /wine-stats command
│   ├── wine-search.md         # /wine-search command
│   └── docker-build.md        # /docker-build command
├── rules/
│   ├── python/                # Python standards
│   │   ├── coding-style.md
│   │   ├── testing.md
│   │   └── security.md
│   └── common/                # General standards
│       ├── git-workflow.md
│       └── performance.md
├── hooks/
│   ├── hooks.json             # Hook configuration
│   ├── session-start.js       # Load context on start
│   └── session-end.js         # Save state on end
├── .claude/
│   └── settings.json          # Claude settings
└── mcp-configs/
    └── mcp-servers.json       # MCP server configs
```

---

## Step-by-Step Implementation

### Step 1: Create AGENTS.md

```markdown
# Wine API SaaS Agents

## Primary Agent
You are an expert full-stack developer specializing in FastAPI, Python, Docker, and SaaS development. 
You build production-ready APIs with security, testing, and CI/CD.

## Subagents

### /agents/planner.md - Feature Planning Agent
When asked to plan a feature:
1. Break down into smallest testable units
2. Identify dependencies
3. Estimate complexity (simple/medium/complex)
4. Create step-by-step implementation plan
5. Include test strategy

### /agents/code-reviewer.md - Code Review Agent
When reviewing code:
1. Check FastAPI best practices
2. Verify security (API keys, rate limiting, input validation)
3. Ensure test coverage
4. Check error handling
5. Verify type hints and documentation

### /agents/tdd-guide.md - TDD Guide Agent
When implementing new features:
1. Write failing test first
2. Implement minimal code to pass test
3. Refactor while keeping tests green
4. Ensure >80% code coverage

### /agents/security-reviewer.md - Security Review Agent
When reviewing security:
1. Check API key handling
2. Verify rate limiting
3. Check for SQL injection (parameterized queries)
4. Verify CORS configuration
5. Check for hardcoded secrets
```

### Step 2: Create CLAUDE.md

```markdown
# Wine API SaaS - Project Context

## Overview
- **Project**: Wine API SaaS - REST API for wine data
- **Tech Stack**: FastAPI, Python 3.12, Pandas, Docker
- **Data**: 32,780 wine records from wine-ratings.csv

## API Endpoints
| Endpoint | Description |
|----------|-------------|
| GET /wines | List wines with pagination & filters |
| GET /wines/{id} | Get single wine |
| GET /wines/search | Full-text search |
| GET /wines/top-rated | Top rated wines |
| GET /wines/stats | Statistics |
| GET /regions | List regions |
| GET /varieties | List varieties |

## Security
- API key authentication (X-API-Key header)
- Rate limiting: 60 req/min
- CORS configurable via ALLOWED_ORIGINS

## Running Locally
```bash
# Without Docker
source venv/bin/activate
uvicorn app.main:app --reload

# With Docker
docker build -t wine-api .
docker run -p 8000:8000 -e API_KEY=your-key wine-api
```

## Testing
```bash
pytest tests/ -v
# 18 tests pass
```

## Key Files
- app/main.py - API endpoints
- app/data.py - CSV data loader
- app/models.py - Pydantic schemas
- tests/test_api.py - API tests
- Dockerfile - Container definition
- docker-compose.yml - Local development
```

### Step 3: Create Skills

#### skills/fastapi-patterns/SKILL.md

```markdown
# FastAPI Patterns Skill

## When to Use
When building or reviewing FastAPI endpoints.

## Best Practices

### Endpoint Structure
```python
@app.get("/endpoint", response_model=ResponseModel)
async def handler(
    param: Type = Query(default, description="..."),
    auth: str = Depends(verify_api_key)
):
    # Business logic
    return response
```

### Error Handling
- Use HTTPException for client errors
- Use custom exceptions with exception handlers
- Always return structured error responses

### Validation
- Use Pydantic models for request/response
- Use Query/Path/Body parameters with validation
- Add field descriptions for OpenAPI docs

### Performance
- Use async/await for I/O operations
- Implement caching for expensive operations
- Use pagination for large datasets
```

#### skills/wine-api-workflow/SKILL.md

```markdown
# Wine API Workflow Skill

## When to Use
When adding new endpoints or features to the wine API.

## Common Tasks

### Adding a New Endpoint
1. Define Pydantic model in app/models.py
2. Add endpoint in app/main.py
3. Add rate limiting decorator
4. Add API key dependency
5. Write tests in tests/test_api.py

### Modifying Data Loading
1. Edit app/data.py
2. Ensure thread-safe global caching
3. Test with test_data.csv
4. Verify with full wine-ratings.csv

### Adding Environment Variables
1. Add to .env.example
2. Add to Dockerfile ENV directive
3. Add to docker-compose.yml
4. Document in CLAUDE.md
```

### Step 4: Create Commands

#### commands/wine-stats.md

```markdown
# /wine-stats

Display statistics about the wine database.

## Usage
/wine-stats

## Output
- Total wines
- Average rating
- Top region
- Rating distribution

## Example
```
Total Wines: 32,780
Average Rating: 91.19
Top Region: Napa Valley, California
Rating Distribution:
  90-94: 25,753
  85-89: 4,492
  95+: 2,535
```
```

#### commands/docker-build.md

```markdown
# /docker-build

Build and run the Docker container.

## Usage
/docker-build          # Build only
/docker-build --run   # Build and run
/docker-build --push  # Build and push to registry

## Options
- --tag: Custom tag (default: latest)
- --port: Port to expose (default: 8000)
```

### Step 5: Create Rules

#### rules/python/coding-style.md

```markdown
# Python Coding Style

## Type Hints
- Always use type hints for function parameters and return types
- Use Optional for nullable types
- Use Union for multiple types

## Example
```python
def get_wine(wine_id: int) -> Wine:
    ...

def list_wines(
    region: Optional[str] = None,
    page: int = Query(1, ge=1)
) -> WineListResponse:
    ...
```

## Naming
- snake_case for functions/variables
- PascalCase for classes
- UPPER_SNAKE_CASE for constants

## Imports
- Group: stdlib, third-party, local
- Sort alphabetically within groups
```

#### rules/python/testing.md

```markdown
# Testing Rules

## Coverage
- Minimum 80% code coverage
- All endpoints must have tests
- All edge cases must be tested

## Test Structure
```python
class TestEndpoint:
    def test_success_case(self, client, auth_headers):
        response = client.get("/endpoint", headers=auth_headers)
        assert response.status_code == 200
    
    def test_auth_required(self, client):
        response = client.get("/endpoint")
        assert response.status_code == 403
    
    def test_not_found(self, client, auth_headers):
        response = client.get("/endpoint/999", headers=auth_headers)
        assert response.status_code == 404
```

## Fixtures
- Use conftest.py for shared fixtures
- Mock external dependencies
- Use meaningful fixture names
```

### Step 6: Create Hooks

#### hooks/hooks.json

```json
{
  "hooks": {
    "PreToolUse": [],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hook": "echo 'File written: ${TOOL_ARGUMENTS}'"
      }
    ],
    "Stop": [
      {
        "matcher": ".*",
        "hook": "echo 'Session ending - saving context'"
      }
    ]
  }
}
```

#### hooks/session-start.js

```javascript
// Session start hook - loads project context
console.log("Loading Wine API SaaS context...");

// Quick validation
const fs = require('fs');
if (fs.existsSync('app/main.py')) {
    console.log("✓ Wine API project detected");
}

// Check for recent changes
const { execSync } = require('child_process');
try {
    const status = execSync('git status --short', { encoding: 'utf8' });
    if (status.trim()) {
        console.log("Recent changes:");
        console.log(status);
    }
} catch (e) {
    // Not a git repo or no changes
}
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| /wine-stats | Display wine database statistics |
| /docker-build | Build Docker container |
| /test | Run test suite |
| /plan | Plan new feature implementation |
| /code-review | Run code review |
| /tdd | Start TDD workflow |

---

## Integration with Claude Code

To use this framework with Claude Code:

1. **Copy rules to ~/.claude/rules/**
   ```bash
   cp -r rules/python ~/.claude/rules/
   ```

2. **Copy hooks to ~/.claude/hooks/**
   ```bash
   cp -r hooks ~/.claude/
   ```

3. **Place AGENTS.md and CLAUDE.md in project root**
   ```bash
   cp AGENTS.md CLAUDE.md wine-api-saas/
   ```

4. **Use slash commands**
   ```
   /wine-stats
   /docker-build
   /test
   ```

---

## Benefits of This Framework

| Benefit | Description |
|---------|-------------|
| **Consistency** | All code follows same standards |
| **Speed** | Reusable skills reduce repetition |
| **Quality** | Rules enforce best practices |
| **Memory** | Hooks preserve context across sessions |
| **Automation** | Commands automate common tasks |
| **Security** | Security rules catch vulnerabilities |

---

## References

- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) - Original framework
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
