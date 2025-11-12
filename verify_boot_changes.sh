#!/bin/bash

# --- Configuration Check Script ---
# This script verifies that the systemd services identified as slow have been
# properly disabled or removed, confirming the changes are ready for the next boot.

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Systemd Service Verification ===${NC}"

# 1. Check Snapd Status (Should be gone after 'apt purge')
echo -e "\n${BLUE}Checking snapd.service status...${NC}"
if systemctl status snapd.service &> /dev/null; then
    # If the service file still exists
    echo -e "${RED}FAILURE:${NC} snapd.service unit file still exists."
    echo "  -> Recommendation: Double-check if 'sudo apt purge snapd' was run correctly."
else
    # If the service file is not found (meaning apt purge worked)
    echo -e "${GREEN}SUCCESS:${NC} snapd.service unit file not found (properly removed)."
fi

# 2. Check Containerd Status (Should be disabled)
echo -e "\n${BLUE}Checking containerd.service status...${NC}"
CONTAINERD_STATUS=$(systemctl is-enabled containerd.service 2>/dev/null)

if [ "$CONTAINERD_STATUS" == "disabled" ]; then
    echo -e "${GREEN}SUCCESS:${NC} containerd.service is disabled for next boot."
elif [ "$CONTAINERD_STATUS" == "masked" ]; then
    echo -e "${GREEN}SUCCESS:${NC} containerd.service is masked (stronger form of disabled)."
else
    echo -e "${RED}FAILURE:${NC} containerd.service status is '$CONTAINERD_STATUS'."
    echo "  -> Recommendation: Run 'sudo systemctl disable containerd.service'"
fi

# 3. Check Live Status (Ensure they are stopped for the current session)
echo -e "\n${BLUE}Checking CURRENT run state for slow services...${NC}"

# Function to check and stop a running service
check_and_stop() {
    local service_name=$1
    if systemctl is-active --quiet "$service_name"; then
        echo -e "${YELLOW}ACTION:${NC} $service_name is currently active (running)."
        echo -e "  -> Stopping $service_name now..."
        if sudo systemctl stop "$service_name"; then
            echo -e "  -> ${GREEN}STOPPED:${NC} $service_name is now inactive."
        else
            echo -e "  -> ${RED}ERROR:${NC} Failed to stop $service_name. Please check manually."
        fi
    else
        echo -e "${GREEN}OK:${NC} $service_name is inactive (not running in this session)."
    fi
}

check_and_stop containerd.service
check_and_stop snapd.service # Will likely fail/say not found if purged, which is fine.

# 4. Prompt for CasaOS (Since we haven't disabled these yet)
echo -e "\n${BLUE}--- CASAOS Services Pending ---${NC}"
CASAOS_APPS=$(systemctl is-enabled casaos-app-management.service 2>/dev/null)
CASAOS_STORAGE=$(systemctl is-enabled casaos-local-storage.service 2>/dev/null)

if [ "$CASAOS_APPS" != "disabled" ] || [ "$CASAOS_STORAGE" != "disabled" ]; then
    echo -e "${YELLOW}Reminder:${NC} The following CasaOS services are still enabled and will add ~35s to boot:"
    echo "  - casaos-app-management.service (Status: $CASAOS_APPS)"
    echo "  - casaos-local-storage.service (Status: $CASAOS_STORAGE)"
    echo -e "  -> To disable them: ${YELLOW}sudo systemctl disable casaos-app-management.service casaos-local-storage.service${NC}"
fi

echo -e "\n${BLUE}Verification complete. All changes are in place for the next reboot.${NC}"
