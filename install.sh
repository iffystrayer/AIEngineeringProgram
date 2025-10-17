#!/bin/bash
# U-AIP Scoping Assistant - Installation Script

set -e

echo "=========================================="
echo "U-AIP Scoping Assistant - Installation"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# Check for uv
echo ""
echo "Checking for uv package manager..."
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv not found. Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"

    if command -v uv &> /dev/null; then
        echo -e "${GREEN}✓ uv installed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  uv installed but not in PATH. You may need to restart your terminal.${NC}"
        echo -e "${YELLOW}   Or run: export PATH=\"\$HOME/.cargo/bin:\$PATH\"${NC}"
    fi
else
    echo -e "${GREEN}✓ uv is installed${NC}"
fi

# Check for Docker
echo ""
echo "Checking for Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. Please install Docker Desktop.${NC}"
    echo "   Download: https://www.docker.com/products/docker-desktop"
else
    echo -e "${GREEN}✓ Docker is installed${NC}"

    # Check if Docker is running
    if ! docker ps &> /dev/null; then
        echo -e "${YELLOW}⚠️  Docker is not running. Please start Docker Desktop.${NC}"
    else
        echo -e "${GREEN}✓ Docker is running${NC}"
    fi
fi

# Install the package
echo ""
echo "Installing U-AIP Scoping Assistant..."
if command -v uv &> /dev/null; then
    uv pip install -e .
else
    pip3 install -e .
fi

# Verify installation
echo ""
echo "Verifying installation..."
if uv run python -c "from src.cli.main import cli; cli(['--help'])" &> /dev/null; then
    echo -e "${GREEN}✓ Package installed successfully${NC}"
else
    echo -e "${RED}❌ Installation verification failed${NC}"
    exit 1
fi

# Check if uaip command is available
echo ""
echo "Checking CLI command availability..."
if command -v uaip &> /dev/null; then
    echo -e "${GREEN}✓ 'uaip' command is available${NC}"
    COMMAND_METHOD="uaip"
else
    echo -e "${YELLOW}⚠️  'uaip' command not in PATH${NC}"
    echo -e "${YELLOW}   You can use: uv run python -m src.cli.main${NC}"
    COMMAND_METHOD="uv run python -m src.cli.main"

    # Offer to create alias
    echo ""
    read -p "Would you like to create a shell alias for 'uaip'? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        SHELL_RC="$HOME/.zshrc"
        if [ -f "$HOME/.bashrc" ]; then
            SHELL_RC="$HOME/.bashrc"
        fi

        echo 'alias uaip="uv run python -m src.cli.main"' >> "$SHELL_RC"
        echo -e "${GREEN}✓ Alias added to $SHELL_RC${NC}"
        echo -e "${YELLOW}   Run: source $SHELL_RC${NC}"
        echo -e "${YELLOW}   Or restart your terminal${NC}"
    fi
fi

# Check for .env file
echo ""
echo "Checking configuration..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:60432/uaip_dev

# LLM Provider (uncomment and set one)
# ANTHROPIC_API_KEY=your-api-key-here
# OLLAMA_BASE_URL=http://localhost:11434

# Optional: Observability
# LANGFUSE_PUBLIC_KEY=your-key
# LANGFUSE_SECRET_KEY=your-secret
# LANGFUSE_HOST=http://localhost:60300
EOF
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}   Please edit .env and add your API keys${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Start database
echo ""
echo "Starting database..."
if docker ps --filter "name=postgres" --format "{{.Names}}" | grep -q "postgres"; then
    echo -e "${GREEN}✓ PostgreSQL database is running${NC}"
else
    if docker ps -a --filter "name=postgres" --format "{{.Names}}" | grep -q "postgres"; then
        echo "Starting existing PostgreSQL container..."
        docker-compose start postgres
    else
        echo "Creating and starting PostgreSQL container..."
        docker-compose up -d postgres
    fi

    echo "Waiting for database to be healthy..."
    sleep 5

    if docker ps --filter "name=postgres" --filter "health=healthy" --format "{{.Names}}" | grep -q "postgres"; then
        echo -e "${GREEN}✓ PostgreSQL database is running and healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Database started but may not be healthy yet${NC}"
        echo -e "${YELLOW}   Check status: docker ps --filter 'name=postgres'${NC}"
    fi
fi

# Summary
echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Set your LLM provider:"
echo "   ${YELLOW}export ANTHROPIC_API_KEY='your-key'${NC}"
echo "   OR"
echo "   ${YELLOW}ollama serve && ollama pull llama3${NC}"
echo ""
echo "2. Verify installation:"
echo "   ${YELLOW}uv run python test_alpha_interactive.py${NC}"
echo ""
echo "3. Start your first session:"
echo "   ${YELLOW}$COMMAND_METHOD start \"your AI project idea\"${NC}"
echo ""
echo "4. Read the quick start guide:"
echo "   ${YELLOW}cat QUICK_START.md${NC}"
echo ""
echo -e "${GREEN}🎉 You're ready to scope AI projects in under an hour!${NC}"
