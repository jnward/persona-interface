#!/bin/bash

echo "================================"
echo "Testing Persona Steering Interface"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if backend is running
echo -n "1. Checking backend (port 8000)... "
if curl -s http://localhost:8000 > /dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo "Please start the backend first: cd backend && python main.py"
    exit 1
fi

# Check if frontend is running
echo -n "2. Checking frontend (port 3000)... "
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo "Please start the frontend first: cd frontend && npm run dev"
    exit 1
fi

# Test backend API
echo -n "3. Testing backend API... "
RESPONSE=$(curl -s -X POST http://localhost:8000/api/generate \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"Hello"}],"steering_config":{"pc_values":{}},"num_tokens":10}')

if echo "$RESPONSE" | grep -q "content"; then
    echo -e "${GREEN}✓ API working${NC}"
else
    echo -e "${RED}✗ API error${NC}"
    echo "Response: $RESPONSE"
fi

echo ""
echo "================================"
echo "All systems operational!"
echo "================================"
echo ""
echo "You can now:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Start chatting with the model"
echo "3. Adjust PC sliders to steer the model behavior"
echo "4. Change token count to control response length"
echo ""
echo "Try these test prompts:"
echo "- 'What are you?' (then adjust PC1 to +3000 and regenerate)"
echo "- 'Tell me a story' (try different PC combinations)"
echo "- 'Count to five' (test with different token counts)"