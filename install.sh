#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Check for success and failure symbols
SUCCESS="✔"
FAILURE="✘"

# Default flag value for --break-system-packages
BREAK_SYSTEM_PACKAGES=""

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --break-system-packages) 
            BREAK_SYSTEM_PACKAGES="--break-system-packages"
            shift
            ;;
        *)
            echo -e "${RED}${FAILURE} Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Update package list and install system dependencies
echo -e "${YELLOW}Updating package list...${NC}"
sudo apt-get update || { echo -e "${RED}${FAILURE} Failed to update package list. ${YELLOW}Try running 'sudo apt-get update' manually.${NC}"; exit 1; }

# Install Python 3 and pip if not already installed
echo -e "${YELLOW}Checking for Python 3 and pip...${NC}"

if ! command_exists python3; then
    echo -e "${YELLOW}Python 3 is not installed. Installing Python 3...${NC}"
    sudo apt-get install -y python3 || { echo -e "${RED}${FAILURE} Failed to install Python 3. ${YELLOW}Check your package manager or internet connection.${NC}"; exit 1; }
else
    echo -e "${GREEN}${SUCCESS} Python 3 is installed.${NC}"
fi

if ! command_exists pip3; then
    echo -e "${YELLOW}pip3 is not installed. Installing pip3...${NC}"
    sudo apt-get install -y python3-pip || { echo -e "${RED}${FAILURE} Failed to install pip3. ${YELLOW}Try running 'sudo apt-get install python3-pip' manually.${NC}"; exit 1; }
else
    echo -e "${GREEN}${SUCCESS} pip3 is installed.${NC}"
fi

# Install required Python packages
echo -e "${YELLOW}Installing required Python packages...${NC}"

pip3 install $BREAK_SYSTEM_PACKAGES selenium webdriver-manager requests beautifulsoup4 python-magic || { echo -e "${RED}${FAILURE} Failed to install Python packages. ${YELLOW}Try running 'pip3 install selenium webdriver-manager requests beautifulsoup4 python-magic' manually.${NC}"; exit 1; }

echo -e "${GREEN}${SUCCESS} Python packages installed.${NC}"

# Install Firefox and GeckoDriver
echo -e "${YELLOW}Checking for Firefox and GeckoDriver...${NC}"

# Install Firefox (if not already installed)
if ! command_exists firefox; then
    echo -e "${YELLOW}Firefox is not installed. Installing Firefox...${NC}"
    sudo apt-get install -y firefox || { echo -e "${RED}${FAILURE} Failed to install Firefox. ${YELLOW}Try running 'sudo apt-get install firefox' manually.${NC}"; exit 1; }
else
    echo -e "${GREEN}${SUCCESS} Firefox is installed.${NC}"
fi

# Install GeckoDriver using webdriver-manager (for automatic management)
echo -e "${YELLOW}Installing GeckoDriver using webdriver-manager...${NC}"
python3 -m webdriver_manager.firefox || { echo -e "${RED}${FAILURE} Failed to install GeckoDriver. ${YELLOW}Try running 'python3 -m webdriver_manager.firefox' manually.${NC}"; exit 1; }

echo -e "${GREEN}${SUCCESS} GeckoDriver installed.${NC}"

# Verify installations
echo -e "${YELLOW}Verifying installations...${NC}"

# Check Python and pip versions
echo -e "${YELLOW}Python version: $(python3 --version)${NC}"
echo -e "${YELLOW}pip3 version: $(pip3 --version)${NC}"

# Check if Firefox is installed
if command_exists firefox; then
    echo -e "${GREEN}${SUCCESS} Firefox version: $(firefox --version)${NC}"
else
    echo -e "${RED}${FAILURE} Firefox is not installed. Please install it manually.${NC}"
    exit 1
fi

# Check if GeckoDriver was installed properly
if command_exists geckodriver; then
    echo -e "${GREEN}${SUCCESS} GeckoDriver version: $(geckodriver --version)${NC}"
else
    echo -e "${RED}${FAILURE} GeckoDriver is not installed. ${YELLOW}Try running 'python3 -m webdriver_manager.firefox' to install it.${NC}"
    exit 1
fi

echo -e "${GREEN}${SUCCESS} Installation completed successfully.${NC}"

# Exit with success
exit 0
