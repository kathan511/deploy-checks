#!/usr/bin/env bash

set -uo pipefail

VERSION="1.0.0"

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

ERRORS=0

fail() {
  echo -e "${RED}❌ $1${NC}"
  ERRORS=$((ERRORS + 1))
}

warn() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

pass() {
  echo -e "${GREEN}✅ $1${NC}"
}

show_help() {
  cat << EOF
deploy-check v${VERSION}
Pre-deployment validation script

Usage: deploy-check [OPTIONS] [VENV_TYPE]

VENV_TYPE:
  1, conda    Check for conda environment (environment.yml)
  2, uv       Check for uv environment (