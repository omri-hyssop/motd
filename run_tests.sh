#!/bin/bash
# Test runner script for MOTD

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  MOTD Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    all)
        echo -e "${YELLOW}Running all tests...${NC}"
        pytest
        ;;
    unit)
        echo -e "${YELLOW}Running unit tests...${NC}"
        pytest tests/unit/ -v
        ;;
    integration)
        echo -e "${YELLOW}Running integration tests...${NC}"
        pytest tests/integration/ -v
        ;;
    auth)
        echo -e "${YELLOW}Running authentication tests...${NC}"
        pytest -k "auth" -v
        ;;
    orders)
        echo -e "${YELLOW}Running order tests...${NC}"
        pytest -k "order" -v
        ;;
    menus)
        echo -e "${YELLOW}Running menu tests...${NC}"
        pytest -k "menu" -v
        ;;
    coverage)
        echo -e "${YELLOW}Running tests with coverage report...${NC}"
        pytest --cov=app --cov-report=html --cov-report=term-missing
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    quick)
        echo -e "${YELLOW}Running quick test suite (no coverage)...${NC}"
        pytest --no-cov -x
        ;;
    failed)
        echo -e "${YELLOW}Re-running failed tests...${NC}"
        pytest --lf -v
        ;;
    verbose)
        echo -e "${YELLOW}Running all tests (verbose)...${NC}"
        pytest -vv -s
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [TYPE]"
        echo ""
        echo "Available types:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  auth         - Run authentication tests"
        echo "  orders       - Run order tests"
        echo "  menus        - Run menu tests"
        echo "  coverage     - Run with detailed coverage report"
        echo "  quick        - Run without coverage (faster)"
        echo "  failed       - Re-run only failed tests"
        echo "  verbose      - Run with verbose output"
        exit 1
        ;;
esac

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✓ All tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  ✗ Some tests failed${NC}"
    echo -e "${RED}========================================${NC}"
fi

exit $EXIT_CODE
