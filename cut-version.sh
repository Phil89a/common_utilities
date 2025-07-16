#!/bin/bash

# This script automates the process of cutting a new version for a Python project,
# building the package, and uploading it to a private PyPI server.
# It updates the version in pyproject.toml, commits the change,
# creates an annotated Git tag, and pushes both the branch and the tag to GitHub.

# --- Configuration ---
REPO_ROOT="/Users/phil/PycharmProjects/common_utilities"
PYPROJECT_TOML="pyproject.toml"
MAIN_BRANCH="main"
REMOTE_NAME="origin"
PYPI_SERVER_URL="http://192.168.85.4:9333/" # Your Debian Dev Host IP and Port
PYPI_USERNAME="phil"       # The username you set with htpasswd
PYPI_PASSWORD="ssh-0918989-wh1tehaven"       # The password you set with htpasswd

# --- Functions ---

# Function to print an error message and exit
error_exit() {
    echo "ERROR: $1" >&2
    exit 1
}

# --- Main Script ---

echo "Starting version cut, build, and upload process..."

# 1. Navigate to the repository root
# This ensures all Git commands are run from the correct directory.
cd "$REPO_ROOT" || error_exit "Could not navigate to $REPO_ROOT. Please check the REPO_ROOT variable in the script."
echo "Navigated to repository: $(pwd)"

# 2. Check for a clean working directory
# It's crucial to have no uncommitted changes to avoid accidental commits or conflicts.
echo "Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    error_exit "Working directory is not clean. Please commit or stash your changes (git status) before cutting a new version."
fi
echo "Working directory is clean."

# 3. Get the new version number from user input
# The script requires one argument: the new version number (e.g., 1.0.1, 2.0.0)
if [ -z "$1" ]; then
    error_exit "Usage: $0 <new_version_number_e.g._1.0.1>"
fi
NEW_VERSION="$1"

# 4. Get the current version from pyproject.toml
# This uses grep to find the version line and awk to extract the version string.
# It assumes the version is in the format 'version = "X.Y.Z"'
CURRENT_VERSION=$(grep 'version =' "$PYPROJECT_TOML" | head -1 | awk -F '"' '{print $2}')
if [ -z "$CURRENT_VERSION" ]; then
    error_exit "Could not find 'version =' in $PYPROJECT_TOML. Ensure the format is 'version = \"X.Y.Z\"'."
fi
echo "Current version in $PYPROJECT_TOML: $CURRENT_VERSION"
echo "New version to set: $NEW_VERSION"

# Check if the new version is the same as the current version
if [ "$CURRENT_VERSION" == "$NEW_VERSION" ]; then
    error_exit "The new version ($NEW_VERSION) is the same as the current version. No change needed."
fi

# 5. Update pyproject.toml with the new version
echo "Updating $PYPROJECT_TOML to version $NEW_VERSION..."
# Using perl for cross-platform (Linux/macOS) in-place editing.
# 's/old/new/' performs the substitution. '-pi -e' means in-place edit, no backup file.
perl -pi -e "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_TOML" || error_exit "Failed to update version in $PYPROJECT_TOML. Check file permissions or format."
echo "$PYPROJECT_TOML updated."

# 6. Stage and commit the version bump
echo "Staging and committing version bump..."
git add "$PYPROJECT_TOML" || error_exit "Failed to stage $PYPROJECT_TOML."
git commit -m "build: Bump version to $NEW_VERSION" || error_exit "Failed to commit version bump."
# Get the hash of the newly created commit
LATEST_COMMIT_HASH=$(git rev-parse HEAD)
echo "New commit created: $LATEST_COMMIT_HASH"

# 7. Delete existing tag if it exists (locally and remotely)
# This prevents conflicts if a tag with the same name already exists but points to an old commit.
echo "Checking for and deleting existing tag '$NEW_VERSION'..."
# Check if local tag exists
if git tag -l | grep -q "^$NEW_VERSION$"; then
    git tag -d "$NEW_VERSION" || error_exit "Failed to delete local tag '$NEW_VERSION'."
    echo "Local tag '$NEW_VERSION' deleted."
fi

# Attempt to delete remote tag. Redirect stderr to /dev/null to suppress "remote ref does not exist" errors.
git push "$REMOTE_NAME" --delete "$NEW_VERSION" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Remote tag '$NEW_VERSION' deleted (if it existed)."
else
    echo "Remote tag '$NEW_VERSION' did not exist or could not be deleted (this is often fine)."
fi

# 8. Create new annotated tag
echo "Creating new annotated tag '$NEW_VERSION' on commit $LATEST_COMMIT_HASH..."
git tag -a "$NEW_VERSION" "$LATEST_COMMIT_HASH" -m "Release $NEW_VERSION" || error_exit "Failed to create new tag '$NEW_VERSION'."
echo "Local tag '$NEW_VERSION' created."

# 9. Push branch and new tag to remote
echo "Pushing '$MAIN_BRANCH' branch to '$REMOTE_NAME'..."
git push "$REMOTE_NAME" "$MAIN_BRANCH" || error_exit "Failed to push '$MAIN_BRANCH' to '$REMOTE_NAME'."
echo "Branch '$MAIN_BRANCH' pushed successfully."

echo "Pushing new tag '$NEW_VERSION' to '$REMOTE_NAME'..."
git push "$REMOTE_NAME" "$NEW_VERSION" || error_exit "Failed to push tag '$NEW_VERSION' to '$REMOTE_NAME'."
echo "Tag '$NEW_VERSION' pushed successfully."

# 10. Build the Python package
echo "Building Python package..."
python -m build --sdist --wheel || error_exit "Failed to build Python package."
echo "Package built successfully in 'dist/' directory."

# 11. Upload the package to the private PyPI server
echo "Uploading package to private PyPI server: $PYPI_SERVER_URL..."
# Using --config-file /dev/null to prevent twine from looking for ~/.pypirc
# and passing credentials directly via environment variables for security.
# The `simple/` endpoint is crucial for pip/twine to work correctly.
env TWINE_USERNAME="$PYPI_USERNAME" TWINE_PASSWORD="$PYPI_PASSWORD" \
twine upload --repository-url "${PYPI_SERVER_URL}simple/" dist/* || error_exit "Failed to upload package to PyPI server."
echo "Package uploaded successfully."

echo "----------------------------------------------------"
echo "Version $NEW_VERSION successfully cut, built, and uploaded!"
echo "Remember to create a GitHub Release from this tag in the GitHub UI (Releases -> Draft a new release -> Select tag)."
echo "----------------------------------------------------"