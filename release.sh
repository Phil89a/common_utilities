#!/bin/bash
set -euo pipefail

# Get version from Python
VERSION=$(python -c "import common_utilities; print(f'v{common_utilities.__version__}')")

# Confirm version tag format
if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version format: $VERSION"
    exit 1
fi

# Add version-related files
git add common_utilities/__init__.py pyproject.toml

# Commit if needed
if ! git diff --cached --quiet; then
    git commit -m "Release $VERSION"
else
    echo "ℹ️ No changes to commit"
fi

# Tag if not already tagged
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo "ℹ️ Tag $VERSION already exists"
else
    git tag "$VERSION"
fi

# Push branch and tag
git push origin main
git push origin "$VERSION"

# Create GitHub release
if command -v gh >/dev/null 2>&1; then
    if gh release view "$VERSION" >/dev/null 2>&1; then
        echo "ℹ️ GitHub release $VERSION already exists"
    else
        gh release create "$VERSION" -t "$VERSION" -n "Auto-release for $VERSION"
    fi
else
    echo "⚠️ GitHub CLI (gh) not found — skipping GitHub release"
fi

echo "✅ Released version $VERSION"