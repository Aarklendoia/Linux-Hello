#!/bin/bash
# Enable Linux Hello facial recognition for PAM services

set -e

PAM_MODULE_PATH="/lib/x86_64-linux-gnu/security/pam_linux_hello.so"

# Check if module exists
if [ ! -f "$PAM_MODULE_PATH" ]; then
    echo "Error: PAM module not found at $PAM_MODULE_PATH"
    exit 1
fi

# Function to enable a service
enable_service() {
    local service=$1
    local pam_file="/etc/pam.d/$service"
    
    if [ ! -f "$pam_file" ]; then
        echo "Warning: PAM file not found: $pam_file"
        return 1
    fi
    
    # Check if already enabled
    if grep -q "pam_linux_hello.so" "$pam_file"; then
        echo "✓ $service: already enabled"
        return 0
    fi
    
    # Backup
    cp "$pam_file" "$pam_file.bak"
    
    # Add module at the beginning of the auth chain
    # Using [default=ignore] for fallback behavior
    sed -i '1{/^@include\|^auth/i auth    [default=ignore]    pam_linux_hello.so\
}' "$pam_file" || {
        # Fallback if sed fails
        (echo "auth    [default=ignore]    pam_linux_hello.so"; cat "$pam_file") > "$pam_file.tmp"
        mv "$pam_file.tmp" "$pam_file"
    }
    
    echo "✓ $service: enabled (backup at $pam_file.bak)"
    return 0
}

# Show usage
if [ $# -eq 0 ]; then
    echo "Usage: $0 <service> [service] ..."
    echo ""
    echo "Available services:"
    ls /etc/pam.d/ | grep -v "^common-\|\.dpkg\|\.bak"
    exit 1
fi

# Enable for each service
for service in "$@"; do
    enable_service "$service" || true
done

echo ""
echo "Done! Test with: sudo pamtester sudo \$USER authenticate"
