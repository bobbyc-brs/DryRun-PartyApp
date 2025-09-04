#!/usr/bin/env python3
"""
Pre-commit setup script for Party Drink Tracker.

This script sets up pre-commit hooks for the project, including:
- Installing pre-commit and development dependencies
- Configuring pre-commit hooks
- Running initial validation

Copyright (C) 2025 Brighter Sight
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

For inquiries, contact: Info@BrighterSight.ca
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_virtual_environment():
    """Check if we're in a virtual environment."""
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  Warning: Not in a virtual environment")
        print("   It's recommended to run this in a virtual environment")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != "y":
            print("   Exiting. Please activate your virtual environment first.")
            sys.exit(1)


def install_dependencies():
    """Install development dependencies."""
    print("\n📦 Installing development dependencies...")

    # Check if requirements-dev.txt exists
    if not Path("requirements-dev.txt").exists():
        print("❌ requirements-dev.txt not found")
        sys.exit(1)

    # Use the same Python executable that's running this script
    python_exe = sys.executable
    pip_exe = python_exe.replace("python", "pip")

    # Install development requirements
    run_command(
        f"{pip_exe} install -r requirements-dev.txt",
        "Installing development dependencies",
    )


def setup_precommit():
    """Set up pre-commit hooks."""
    print("\n🪝 Setting up pre-commit hooks...")

    # Check if .pre-commit-config.yaml exists
    if not Path(".pre-commit-config.yaml").exists():
        print("❌ .pre-commit-config.yaml not found")
        sys.exit(1)

    # Use the same Python executable that's running this script
    python_exe = sys.executable
    precommit_exe = python_exe.replace("python", "pre-commit")

    # Install pre-commit hooks
    run_command(f"{precommit_exe} install", "Installing pre-commit hooks")

    # Install pre-commit hooks for commit messages
    run_command(
        f"{precommit_exe} install --hook-type commit-msg",
        "Installing commit message hooks",
    )


def run_initial_validation():
    """Run initial validation to ensure everything works."""
    print("\n🧪 Running initial validation...")

    # Use the same Python executable that's running this script
    python_exe = sys.executable
    precommit_exe = python_exe.replace("python", "pre-commit")

    # Run pre-commit on all files
    print("🔄 Running pre-commit on all files (this may take a while)...")
    result = run_command(
        f"{precommit_exe} run --all-files", "Running pre-commit validation", check=False
    )

    if result.returncode == 0:
        print("✅ All pre-commit checks passed!")
    else:
        print("⚠️  Some pre-commit checks failed. This is normal for the first run.")
        print("   The hooks will fix many issues automatically.")
        print("   Review the output above and commit the changes.")


def create_gitignore_additions():
    """Add pre-commit related entries to .gitignore if needed."""
    gitignore_path = Path(".gitignore")
    additions = [
        "",
        "# Pre-commit and development files",
        "bandit-report.json",
        ".coverage",
        "htmlcov/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".tox/",
        "dist/",
        "build/",
        "*.egg-info/",
    ]

    if gitignore_path.exists():
        content = gitignore_path.read_text()
        for addition in additions:
            if addition not in content:
                content += addition + "\n"
        gitignore_path.write_text(content)
        print("✅ Updated .gitignore with pre-commit related entries")


def main():
    """Main setup function."""
    print("🍻 Party Drink Tracker - Pre-commit Setup")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("app").exists() or not Path("requirements.txt").exists():
        print("❌ This doesn't appear to be the Party Drink Tracker project directory")
        print("   Please run this script from the project root")
        sys.exit(1)

    # Check virtual environment
    check_virtual_environment()

    # Install dependencies
    install_dependencies()

    # Set up pre-commit
    setup_precommit()

    # Update .gitignore
    create_gitignore_additions()

    # Run initial validation
    run_initial_validation()

    print("\n🎉 Pre-commit setup complete!")
    print("\nNext steps:")
    print("1. Review any changes made by the pre-commit hooks")
    print("2. Commit the changes: git add . && git commit -m 'Setup pre-commit hooks'")
    print("3. The hooks will now run automatically on every commit")
    print("\nTo run hooks manually:")
    print("  pre-commit run --all-files    # Run on all files")
    print("  pre-commit run                # Run on staged files only")


if __name__ == "__main__":
    main()
