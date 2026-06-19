#!/bin/bash

# Define colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}Starting Mental Health Companion App...${NC}"
echo -e "${BLUE}==========================================${NC}"

# Kill any existing processes on the ports to avoid conflicts
echo "Cleaning up any old processes..."
fuser -k 8000/tcp 2>/dev/null
fuser -k 8083/tcp 2>/dev/null

# Start the backend in the background
echo -e "${GREEN}Starting backend server on port 8000...${NC}"
cd backend
uv run run.py &
BACKEND_PID=$!
cd ..

# Start the frontend in the background
echo -e "${GREEN}Starting frontend server on port 8083...${NC}"
cd frontend
python3 -m http.server 8083 &
FRONTEND_PID=$!
cd ..

echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}✅ App is now running!${NC}"
echo -e "${GREEN}🌐 Frontend UI: http://localhost:8083${NC}"
echo -e "${GREEN}⚙️  Backend API: http://localhost:8000${NC}"
echo -e "${RED}Press Ctrl+C to stop both servers safely.${NC}"
echo -e "${BLUE}==========================================${NC}"

# Trap Ctrl+C to kill both background processes cleanly
trap "echo -e '\n${RED}Stopping servers...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Keep script running to listen for Ctrl+C
wait $BACKEND_PID $FRONTEND_PID
