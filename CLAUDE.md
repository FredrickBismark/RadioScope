# CLAUDE.md — RadioScope

This file provides guidance to Claude and other AI coding assistants working in this repository.

---

## Project Overview

**RadioScope** is a radio analysis application. This repository is in its initial state — no source code has been committed yet. As the codebase grows, this file should be updated to reflect the actual structure, stack, and conventions in use.

---

## Repository State

- **Status**: Freshly initialized — no source files committed yet.
- **Primary branch**: `main` (or as established by the first commit)
- **Remote**: `FredrickBismark/RadioScope`

---

## Development Branch Conventions

- Feature branches follow the pattern: `feature/<short-description>`
- AI-assisted branches follow: `claude/<task-slug>`
- Bug-fix branches: `fix/<issue-description>`
- Never commit directly to `main` without a pull request review.
- Always push to the branch specified at the top of the session task.

---

## Git Workflow

```bash
# Start work on a new feature
git checkout -b feature/my-feature

# Stage and commit with a descriptive message
git add <specific-files>
git commit -m "feat: describe what this commit does"

# Push to remote
git push -u origin feature/my-feature
```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix     | Use for                                      |
|------------|----------------------------------------------|
| `feat:`    | New feature                                  |
| `fix:`     | Bug fix                                      |
| `docs:`    | Documentation only changes                   |
| `refactor:`| Code change that neither fixes a bug nor adds a feature |
| `test:`    | Adding or updating tests                     |
| `chore:`   | Build process, dependency updates, tooling   |
| `perf:`    | Performance improvements                     |

Examples:
```
feat: add frequency spectrum waterfall display
fix: correct FFT window size calculation
docs: update CLAUDE.md with build instructions
test: add unit tests for signal parser
```

---

## Project Structure (To Be Established)

Once source code is added, update this section with the actual layout. Expected structure:

```
RadioScope/
├── CLAUDE.md               # This file
├── README.md               # User-facing documentation
├── .gitignore              # Git ignore rules
├── package.json            # (if Node.js / JS project)
├── src/                    # Source code
│   ├── main.*              # Application entry point
│   ├── components/         # UI components (if applicable)
│   ├── services/           # Business logic / data services
│   └── utils/              # Shared utility functions
├── tests/                  # Test files
│   ├── unit/
│   └── integration/
├── docs/                   # Extended documentation
└── scripts/                # Build, deploy, utility scripts
```

> **Update this section** once the actual directory layout is decided and implemented.

---

## Technology Stack

> **To be filled in** once the stack is chosen. Common options for radio/signal analysis applications:

| Layer         | Likely Options                          |
|---------------|-----------------------------------------|
| Language      | Python, TypeScript/JavaScript, Rust, C++ |
| UI Framework  | React, Vue, Svelte, Qt, wxWidgets       |
| Signal Proc.  | NumPy/SciPy, WebAssembly, FFTW          |
| SDR Backend   | GNU Radio, librtlsdr, SoapySDR          |
| Testing       | pytest, Jest, Vitest, cargo test        |
| Build Tool    | vite, webpack, CMake, cargo             |

---

## Development Setup

> **To be filled in** once the project is initialized. This section should eventually include:

```bash
# Install dependencies
<package-manager> install

# Run in development mode
<package-manager> run dev

# Run tests
<package-manager> run test

# Build for production
<package-manager> run build
```

### Prerequisites

Document here:
- Required runtime versions (Node.js >=X, Python >=X, Rust stable, etc.)
- System-level dependencies (librtlsdr, portaudio, etc.)
- Environment variables or `.env` setup

---

## Testing Conventions

- **All new features must include tests.**
- Tests live alongside source files or in a dedicated `tests/` directory.
- Follow the Arrange-Act-Assert (AAA) pattern.
- Test file naming: `<module>.test.<ext>` or `test_<module>.<ext>`.
- Aim for unit tests on pure logic and integration tests for I/O-heavy code.

### Running Tests

```bash
# Update with actual commands once the stack is set
<test-command>
```

---

## Code Conventions

### General

- Keep functions small and focused on a single responsibility.
- Prefer explicit over implicit — no magic numbers or unexplained constants.
- Document non-obvious logic with inline comments; avoid obvious comments.
- Delete dead code rather than commenting it out.
- Avoid over-engineering: build the minimum needed for the current task.

### Naming

| Construct       | Convention (adjust for language)          |
|-----------------|-------------------------------------------|
| Variables       | `camelCase` (JS/TS) / `snake_case` (Py)  |
| Functions       | `camelCase` / `snake_case`                |
| Classes         | `PascalCase`                              |
| Constants       | `UPPER_SNAKE_CASE`                        |
| Files/modules   | `kebab-case` (JS/TS) / `snake_case` (Py) |

### Imports

- Group imports: standard library → third-party → internal.
- Avoid circular dependencies.
- Use absolute imports over relative when the project structure supports it.

### Error Handling

- Handle errors at the boundary (user input, external APIs, hardware I/O).
- Do not swallow exceptions silently — log or surface them.
- Avoid adding error handling for scenarios that cannot happen in practice.

---

## AI Assistant Instructions

When working in this repository, Claude and other AI assistants should:

1. **Read before writing** — Always read a file before editing it. Understand existing code before proposing changes.
2. **Stay focused** — Only make changes directly requested or clearly necessary. Do not refactor unrelated code.
3. **No unnecessary files** — Do not create files unless required. Prefer editing existing files.
4. **No over-engineering** — Three similar lines of code is better than a premature abstraction.
5. **Security first** — Never introduce command injection, XSS, SQL injection, or other OWASP Top 10 vulnerabilities.
6. **Commit atomically** — One logical change per commit; use descriptive conventional commit messages.
7. **Branch discipline** — Always develop on the specified branch. Never push to `main` directly.
8. **Test your work** — Run existing tests after changes; add tests for new logic.
9. **Update this file** — If you establish new patterns, add dependencies, or restructure the project, update CLAUDE.md to reflect the new state.
10. **Ask when unclear** — If requirements are ambiguous, prefer asking over guessing.

### What NOT to Do

- Do not add docstrings or comments to code you did not change.
- Do not add fallback or validation for impossible scenarios.
- Do not create helpers for one-off operations.
- Do not use feature flags or backwards-compatibility shims when direct change is appropriate.
- Do not push to a branch other than the one specified for the task.

---

## Sensitive Information

- Do not commit `.env` files, API keys, hardware credentials, or personal data.
- Add secrets management instructions here once established (e.g., `.env.example` with placeholder values).

---

## Updating This File

This document should be treated as a living specification. Update it when:

- The technology stack is finalized.
- A new major directory or module is added.
- A new workflow or convention is established.
- Tooling (CI, linting, formatting) is configured.
- Prerequisites or setup steps change.

Keep it accurate — an outdated CLAUDE.md is worse than none.
