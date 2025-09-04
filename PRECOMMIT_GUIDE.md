# 🪝 Pre-Commit Hooks Setup Guide

## Overview

Pre-commit hooks are scripts that run automatically before each commit to ensure code quality, consistency, and prevent common issues. This guide explains how to set up and use pre-commit hooks for the Party Drink Tracker project.

## What Are Pre-Commit Hooks?

Pre-commit hooks are automated checks that run before you commit code to Git. They can:
- Format code automatically
- Check for syntax errors
- Run tests
- Check for security vulnerabilities
- Ensure consistent coding style
- Prevent large files from being committed

## Quick Setup

### 1. Install Pre-Commit
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install
```

### 2. Run on All Files (First Time)
```bash
# This will run all hooks on all files
pre-commit run --all-files
```

## What Hooks Are Configured?

### 🔧 **Code Formatting**
- **Black**: Automatically formats Python code
- **isort**: Sorts and organizes imports

### 🔍 **Code Quality**
- **flake8**: Lints Python code for style and errors
- **bandit**: Checks for security vulnerabilities

### 🧪 **Testing**
- **pytest**: Runs your test suite
- **coverage**: Ensures test coverage requirements are met

### 📁 **File Checks**
- **trailing-whitespace**: Removes trailing spaces
- **end-of-file-fixer**: Ensures files end with newlines
- **check-yaml**: Validates YAML files
- **check-json**: Validates JSON files
- **check-merge-conflict**: Prevents merge conflict markers
- **check-added-large-files**: Prevents large files (>1MB)

## How to Use

### Automatic Usage
Once installed, hooks run automatically on every commit:
```bash
git add .
git commit -m "Your commit message"
# Hooks run automatically here
```

### Manual Usage
```bash
# Run on staged files only
pre-commit run

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black
pre-commit run flake8
```

### Skip Hooks (Emergency Only)
```bash
# Skip all hooks (not recommended)
git commit --no-verify -m "Emergency commit"

# Skip specific hook
SKIP=flake8 git commit -m "Skip flake8 for this commit"
```

## Common Issues and Solutions

### 1. **Black Formatting Conflicts**
If Black changes your code formatting:
```bash
# Let Black fix it automatically
pre-commit run black --all-files
git add .
git commit -m "Fix code formatting"
```

### 2. **Import Sorting Issues**
If isort changes your imports:
```bash
# Let isort fix it automatically
pre-commit run isort --all-files
git add .
git commit -m "Fix import sorting"
```

### 3. **Test Failures**
If tests fail:
```bash
# Run tests manually to see details
python -m pytest tests/ -v

# Fix the issues, then commit
git add .
git commit -m "Fix failing tests"
```

### 4. **Security Issues**
If bandit finds security issues:
```bash
# Review the issues
pre-commit run bandit --all-files

# Fix the issues in your code
# Then commit again
```

## Configuration Files

### `.pre-commit-config.yaml`
Main configuration file that defines which hooks to run.

### `.flake8`
Configuration for flake8 linting rules.

### `pyproject.toml`
Modern Python project configuration including tool settings.

## Customization

### Adding New Hooks
Edit `.pre-commit-config.yaml` to add new hooks:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: your-new-hook
```

### Modifying Existing Hooks
Edit the configuration files to change hook behavior:
- `.flake8` for flake8 settings
- `pyproject.toml` for Black, isort, and other tools

## Best Practices

### 1. **Run Hooks Frequently**
```bash
# Run before committing
pre-commit run

# Run on all files weekly
pre-commit run --all-files
```

### 2. **Fix Issues Immediately**
Don't let formatting or linting issues accumulate. Fix them as they appear.

### 3. **Use Meaningful Commit Messages**
Even with automated formatting, write clear commit messages.

### 4. **Keep Hooks Updated**
```bash
# Update hook versions
pre-commit autoupdate
```

## Troubleshooting

### Hook Installation Issues
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Performance Issues
If hooks are slow:
```bash
# Run only on changed files
pre-commit run

# Or run specific hooks
pre-commit run black flake8
```

### Virtual Environment Issues
Make sure you're in the correct virtual environment:
```bash
# Check current environment
which python
which pre-commit

# Should point to your venv directory
```

## Integration with CI/CD

The same hooks can be run in CI/CD pipelines:
```yaml
# Example GitHub Actions
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
```

## Benefits

✅ **Consistent Code Style**: All team members follow the same formatting rules
✅ **Early Error Detection**: Catch issues before they reach the repository
✅ **Security Scanning**: Automatically check for common security issues
✅ **Test Coverage**: Ensure tests pass and coverage requirements are met
✅ **File Quality**: Prevent large files and merge conflicts

## Support

If you encounter issues:
1. Check this guide first
2. Run `pre-commit run --all-files` to see detailed output
3. Check the pre-commit documentation: https://pre-commit.com/
4. Review the specific tool documentation (Black, flake8, etc.)

---

**Remember**: Pre-commit hooks are your friends! They help maintain code quality and catch issues early. Embrace them! 🚀
