#!/usr/bin/env bash
set -euo pipefail

# Colors
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo -e "${GREEN}🚀 Installing deploy-check...${NC}"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python 3.10+ is required (found: $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Determine install method
if command -v pipx &> /dev/null; then
    echo -e "${YELLOW}📦 Installing via pipx...${NC}"
    pipx install git+https://github.com/Kathan511/deploy-checks.git
elif command -v uv &> /dev/null; then
    echo -e "${YELLOW}📦 Installing via uv...${NC}"
    uv tool install git+https://github.com/Kathan511/deploy-checks.git
elif command -v pip &> /dev/null; then
    echo -e "${YELLOW}📦 Installing via pip...${NC}"
    pip install --user git+https://github.com/Kathan511/deploy-checks.git
else
    echo -e "${RED}❌ No package manager found (pipx, uv, or pip required)${NC}"
    exit 1
fi

# Verify installation
if command -v deploy-check &> /dev/null; then
    echo -e "${GREEN}✅ deploy-check installed successfully!${NC}"
    echo ""
    echo "Usage:"
    echo "  deploy-check          # Run in current directory"
    echo "  deploy-check /path    # Run in specific directory"
    echo ""
    echo "To setup git hook in a repo:"
    echo "  echo -e '#!/bin/bash\ndeploy-check' > .git/hooks/pre-push"
    echo "  chmod +x .git/hooks/pre-push"
else
    echo -e "${YELLOW}⚠️  Installed but 'deploy-check' not in PATH${NC}"
    echo "Add ~/.local/bin to your PATH:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
fi
