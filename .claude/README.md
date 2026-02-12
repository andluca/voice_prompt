# .claude Directory

This directory contains Claude Code-specific files to help with development.

## Structure

```
.claude/
├── CLAUDE.md              # Main project context for Claude Code
├── skills/                # Reusable knowledge and best practices
│   ├── python-best-practices.md
│   └── cross-platform-development.md
└── commands/              # Development workflow commands
    ├── spec               # View specification
    ├── test               # Run tests
    ├── status             # Check project status
    └── build              # Build specific components
```

## Files

### CLAUDE.md
Main project context document. Contains:
- Project overview and goals
- Architecture and component structure
- Technical stack and library choices
- Development workflow
- Current status and next steps
- Critical implementation notes

Claude Code reads this file to understand the project context.

### skills/

#### python-best-practices.md
Python coding standards for this project:
- Code style and formatting
- Error handling patterns
- Class design principles
- Logging best practices
- Testing approaches
- Common anti-patterns to avoid

#### cross-platform-development.md
Cross-platform development guidelines:
- Path handling (Linux + Windows)
- Platform detection
- Audio recording
- Keyboard handling
- File system operations
- Installation scripts

### commands/

Development workflow helper scripts.

#### spec
View the project specification (SPEC.md) in your terminal.

```bash
./.claude/commands/spec
```

#### test
Run the test suite with coverage.

```bash
# Run all tests
./.claude/commands/test

# Run specific test file
./.claude/commands/test tests/test_config.py

# Run with verbose output
./.claude/commands/test -v
```

#### status
Check project status - what's implemented, what's missing.

```bash
./.claude/commands/status
```

Shows:
- ✅/❌ for each key file
- Dependency installation status
- Test coverage
- TODO progress

#### build
Get context for building a specific component.

```bash
# List available components
./.claude/commands/build

# Get context for building a component
./.claude/commands/build config
./.claude/commands/build recorder
./.claude/commands/build transcriber
```

Shows:
- Requirements from SPEC.md
- Files to create
- Key features to implement
- Relevant skills to reference

## Usage with Claude Code

### Starting a new task
```bash
# Check what needs to be done
./.claude/commands/status

# Read the spec for a component
./.claude/commands/build config

# Then work with Claude Code
claude-code "Implement ConfigManager as specified in TODO.md Phase 2.1"
```

### During development
```bash
# Run tests frequently
./.claude/commands/test

# Check overall status
./.claude/commands/status

# Reference the spec
./.claude/commands/spec
```

### Key workflow
1. **Check status** - See what's done and what's next
2. **Read spec** - Understand requirements for the component
3. **Reference skills** - Follow best practices
4. **Build** - Let Claude Code implement with full context
5. **Test** - Verify implementation works
6. **Iterate** - Refine based on test results

## Why This Structure?

### Separation of Concerns
- **CLAUDE.md**: High-level context, current state
- **skills/**: Reusable knowledge, patterns
- **commands/**: Practical workflow helpers

### Claude Code Integration
Claude Code automatically:
1. Reads `.claude/CLAUDE.md` for project context
2. Can reference skills when needed
3. Benefits from having all context in one place

### Developer Experience
The commands provide quick access to:
- Project documentation (without leaving terminal)
- Test execution
- Status checks
- Component-specific context

## Updating These Files

### When to update CLAUDE.md
- Major architectural decisions
- Phase transitions
- Important implementation notes
- Current blockers or questions

### When to update skills/
- New patterns discovered
- Common mistakes to avoid
- Library-specific gotchas
- Cross-platform issues found

### When to add commands/
- Repetitive workflow steps
- Complex multi-step processes
- Project-specific shortcuts

## Best Practices

1. **Keep CLAUDE.md current** - Update after major changes
2. **Reference skills in prompts** - "Use patterns from python-best-practices.md"
3. **Use commands regularly** - They save time and provide context
4. **Add new skills as needed** - Document what you learn

## Examples

### Good Claude Code prompt with context
```bash
claude-code "Implement ConfigManager following the patterns in 
.claude/skills/python-best-practices.md, specifically the 
'Defaults + Overrides Pattern' section"
```

### Using commands in workflow
```bash
# 1. Check what's next
./.claude/commands/status

# 2. Get component context
./.claude/commands/build config

# 3. Implement
claude-code "Build ConfigManager for Phase 2.1"

# 4. Test
./.claude/commands/test tests/test_config.py

# 5. Verify
./.claude/commands/status
```
