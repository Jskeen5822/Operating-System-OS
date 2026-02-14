#!/bin/bash



set -e

echo "Building Operating System OS..."
make clean
make build

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
    echo ""
    echo "To run the OS in QEMU, execute:"
    echo "  qemu-system-i386 -kernel build/bin/os.bin"
    echo ""
    echo "Alternatively, use:"
    echo "  make run"
    echo ""
else
    echo "✗ Build failed!"
    exit 1
fi
