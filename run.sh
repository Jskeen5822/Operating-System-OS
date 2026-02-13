#!/bin/bash

# Operating System OS - Universal Launcher Script
# Usage: ./run.sh [desktop|simulator|build|clean]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to show help
show_help() {
    cat << EOF
${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${GREEN}  Operating System OS - Launcher${NC}
${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${YELLOW}USAGE:${NC}
  ./run.sh [COMMAND]

${YELLOW}COMMANDS:${NC}
  ${GREEN}desktop${NC}      Launch the full graphical desktop (RECOMMENDED) ⭐
  ${GREEN}simulator${NC}    Launch the CLI simulator
  ${GREEN}build${NC}        Build the native kernel binary
  ${GREEN}clean${NC}        Clean build artifacts
  ${GREEN}help${NC}         Show this help message

${YELLOW}EXAMPLES:${NC}
  ./run.sh desktop       # Launch desktop environment
  ./run.sh simulator     # Launch CLI simulator
  ./run.sh build         # Build native kernel
  ./run.sh clean         # Clean build files

${YELLOW}DEFAULT:${NC}
  If no command is specified, launches the desktop environment.

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
EOF
}

# Function to launch desktop
launch_desktop() {
    print_info "Launching graphical desktop environment..."
    
    # Check if Tkinter is available
    if ! python3 -c "import tkinter" 2>/dev/null; then
        print_error "Tkinter not found"
        print_info "Install with:"
        print_info "  Ubuntu/Debian: sudo apt-get install python3-tk"
        print_info "  macOS: brew install python-tk"
        print_info "  Windows: python -m pip install tk"
        exit 1
    fi
    
    if [ ! -f "desktop.py" ]; then
        print_error "desktop.py not found"
        exit 1
    fi
    
    sleep 1
    print_success "Desktop environment ready!"
    echo ""
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo "  • Click Terminal to run commands"
    echo "  • Click File Manager to browse files"
    echo "  • Click System Monitor to view processes"
    echo "  • Try: exec process1, exec process2, ps"
    echo ""
    
    python3 desktop.py
}

# Function to launch simulator
launch_simulator() {
    print_info "Launching CLI simulator..."
    
    if [ ! -f "simulator.py" ]; then
        print_error "simulator.py not found"
        exit 1
    fi
    
    sleep 1
    print_success "Simulator starting..."
    echo ""
    
    python3 simulator.py
}

# Function to build kernel
build_kernel() {
    print_info "Building native kernel..."
    
    if [ ! -f "Makefile" ]; then
        print_error "Makefile not found"
        exit 1
    fi
    
    # Check for required tools
    if ! command -v gcc &> /dev/null; then
        print_error "GCC not found"
        print_info "Install with: sudo apt-get install build-essential"
        exit 1
    fi
    
    if ! command -v nasm &> /dev/null; then
        print_error "NASM not found"
        print_info "Install with: sudo apt-get install nasm"
        exit 1
    fi
    
    print_info "Starting build..."
    if make clean && make build; then
        print_success "Build completed successfully!"
        if [ -f "build/bin/os.bin" ]; then
            SIZE=$(du -h build/bin/os.bin | cut -f1)
            print_success "Kernel created: build/bin/os.bin ($SIZE)"
        fi
    else
        print_error "Build failed"
        exit 1
    fi
}

# Function to clean build
clean_build() {
    print_info "Cleaning build artifacts..."
    
    if [ ! -f "Makefile" ]; then
        print_error "Makefile not found"
        exit 1
    fi
    
    make clean
    print_success "Build cleaned successfully!"
}

# Main script logic
COMMAND="${1:-desktop}"

case "$COMMAND" in
    desktop)
        launch_desktop
        ;;
    simulator)
        launch_simulator
        ;;
    build)
        build_kernel
        ;;
    clean)
        clean_build
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac
