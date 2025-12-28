#!/bin/bash
# Game Planner - Global OpenCode Installation Script (Unix/Linux/Mac)
# This script installs game-planner commands and agents to your global OpenCode config

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Game Planner Installer${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Determine OpenCode config directory
# Priority: ~/.opencode > ~/.config/opencode
if [ -d "$HOME/.opencode" ]; then
    OPENCODE_DIR="$HOME/.opencode"
elif [ -d "$HOME/.config/opencode" ]; then
    OPENCODE_DIR="$HOME/.config/opencode"
else
    # Create default location
    OPENCODE_DIR="$HOME/.opencode"
fi

echo -e "${YELLOW}Target directory:${NC} $OPENCODE_DIR"

# Get script directory (where game-planner is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source files
AGENT_DIR="$SCRIPT_DIR/.opencode/agent"
COMMAND_DIR="$SCRIPT_DIR/.opencode/command"

# Check source files exist
if [ ! -f "$AGENT_DIR/game-designer.yaml" ]; then
    echo -e "${RED}Error: game-designer.yaml not found at $AGENT_DIR${NC}"
    exit 1
fi

if [ ! -f "$AGENT_DIR/game-reviewer.yaml" ]; then
    echo -e "${RED}Error: game-reviewer.yaml not found at $AGENT_DIR${NC}"
    exit 1
fi

if [ ! -f "$COMMAND_DIR/GamePlan.md" ]; then
    echo -e "${RED}Error: GamePlan.md not found at $COMMAND_DIR${NC}"
    exit 1
fi

# Create target directories if they don't exist
mkdir -p "$OPENCODE_DIR/agent"
mkdir -p "$OPENCODE_DIR/command"

# Backup existing files if they exist
backup_if_exists() {
    local file="$1"
    if [ -f "$file" ]; then
        local backup="${file}.backup.$(date +%Y%m%d%H%M%S)"
        echo -e "${YELLOW}Backing up existing file:${NC} $file -> $backup"
        cp "$file" "$backup"
    fi
}

# Install agent files
echo ""
echo -e "${GREEN}Installing agent configurations...${NC}"

backup_if_exists "$OPENCODE_DIR/agent/game-designer.yaml"
cp "$AGENT_DIR/game-designer.yaml" "$OPENCODE_DIR/agent/"
echo -e "  ${GREEN}[OK]${NC} game-designer.yaml"

backup_if_exists "$OPENCODE_DIR/agent/game-reviewer.yaml"
cp "$AGENT_DIR/game-reviewer.yaml" "$OPENCODE_DIR/agent/"
echo -e "  ${GREEN}[OK]${NC} game-reviewer.yaml"

# Install command file
echo ""
echo -e "${GREEN}Installing slash command...${NC}"

backup_if_exists "$OPENCODE_DIR/command/GamePlan.md"
cp "$COMMAND_DIR/GamePlan.md" "$OPENCODE_DIR/command/"
echo -e "  ${GREEN}[OK]${NC} GamePlan.md (/GamePlan command)"

# Verify installation
echo ""
echo -e "${GREEN}Verifying installation...${NC}"

verify_file() {
    local file="$1"
    local name="$2"
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}[OK]${NC} $name"
        return 0
    else
        echo -e "  ${RED}[FAIL]${NC} $name"
        return 1
    fi
}

VERIFY_SUCCESS=true
verify_file "$OPENCODE_DIR/agent/game-designer.yaml" "game-designer agent" || VERIFY_SUCCESS=false
verify_file "$OPENCODE_DIR/agent/game-reviewer.yaml" "game-reviewer agent" || VERIFY_SUCCESS=false
verify_file "$OPENCODE_DIR/command/GamePlan.md" "/GamePlan command" || VERIFY_SUCCESS=false

echo ""
if [ "$VERIFY_SUCCESS" = true ]; then
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "You can now use the ${BLUE}/GamePlan${NC} command in OpenCode:"
    echo ""
    echo -e "  ${YELLOW}opencode -c${NC}              # Start OpenCode"
    echo -e "  ${YELLOW}/GamePlan zombie roguelike${NC}  # Generate GDD"
    echo ""
    echo -e "Files installed to: ${BLUE}$OPENCODE_DIR${NC}"
else
    echo -e "${RED}================================${NC}"
    echo -e "${RED}  Installation Failed!${NC}"
    echo -e "${RED}================================${NC}"
    echo ""
    echo "Please check the error messages above and try again."
    exit 1
fi
