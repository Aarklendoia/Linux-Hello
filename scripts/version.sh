#!/bin/bash
# Helper script for semantic versioning and releases
# Usage: ./scripts/version.sh [major|minor|patch|VERSION]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current version from git tags (only the version number, not the commits after)
CURRENT_VERSION=$(git describe --tags --match '[0-9]*.[0-9]*.[0-9]*' --abbrev=0 2>/dev/null || echo "0.0.0")
echo "Current version: $CURRENT_VERSION"

# Parse version components - remove any leading 'v' and handle git describe format
VERSION_CLEAN=$(echo "$CURRENT_VERSION" | sed 's/v//' | cut -d'-' -f1)
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION_CLEAN"
MAJOR=${MAJOR:-0}
MINOR=${MINOR:-0}
PATCH=${PATCH:-0}

# Function to show usage
show_usage() {
    cat << EOF
${GREEN}Linux Hello - Semantic Versioning Helper${NC}

Usage: $0 [COMMAND]

Commands:
  major          Bump major version (1.0.0 → 2.0.0)
  minor          Bump minor version (1.0.0 → 1.1.0)
  patch          Bump patch version (1.0.0 → 1.0.1)
  VERSION        Set specific version (e.g., 1.2.3)
  show           Show current version
  help           Show this help message

Examples:
  $0 patch                    # Create tag 1.0.1
  $0 minor                    # Create tag 1.1.0
  $0 1.5.0                    # Create tag 1.5.0

EOF
}

# Function to validate semver format
validate_semver() {
    if [[ ! $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}✗ Invalid version format: $1${NC}"
        echo "  Expected format: MAJOR.MINOR.PATCH (e.g., 1.2.3)"
        exit 1
    fi
}

# Function to create tag
create_tag() {
    local new_version=$1
    validate_semver "$new_version"
    
    echo -e "${YELLOW}Creating release tag: $new_version${NC}"
    
    # Check if tag already exists
    if git rev-parse "refs/tags/$new_version" >/dev/null 2>&1; then
        echo -e "${RED}✗ Tag $new_version already exists${NC}"
        exit 1
    fi
    
    # Create signed tag
    git tag -s -m "Release $new_version" "$new_version"
    
    echo -e "${GREEN}✓ Tag created: $new_version${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Review changes: git log $(git describe --tags --abbrev=0 2>/dev/null || echo 'HEAD~1')..HEAD"
    echo "  2. Push tags:     git push origin $new_version"
    echo "  3. GitHub Actions will automatically build and create a release"
    echo ""
    echo -e "${GREEN}View at:${NC} https://github.com/yourusername/linux-hello/releases"
}

# Main logic
case "${1:-show}" in
    major)
        NEW_VERSION=$((MAJOR + 1)).0.0
        create_tag "$NEW_VERSION"
        ;;
    minor)
        NEW_VERSION=$MAJOR.$((MINOR + 1)).0
        create_tag "$NEW_VERSION"
        ;;
    patch)
        NEW_VERSION=$MAJOR.$MINOR.$((PATCH + 1))
        create_tag "$NEW_VERSION"
        ;;
    show)
        echo -e "${GREEN}Current version: $CURRENT_VERSION${NC}"
        echo ""
        echo "Next versions:"
        echo "  Major: $((MAJOR + 1)).0.0"
        echo "  Minor: $MAJOR.$((MINOR + 1)).0"
        echo "  Patch: $MAJOR.$MINOR.$((PATCH + 1))"
        ;;
    help|--help|-h)
        show_usage
        ;;
    [0-9]*.[0-9]*.[0-9]*)
        create_tag "$1"
        ;;
    *)
        echo -e "${RED}✗ Unknown command: $1${NC}"
        show_usage
        exit 1
        ;;
esac
