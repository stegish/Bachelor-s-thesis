#!/bin/sh

# Replace env vars in JavaScript files
echo "Replacing env vars..."

# Create a runtime env.js file
cat > /usr/share/nginx/html/env.js <<EOF
window.env = {
  REACT_APP_ANALYTICS_API: "${REACT_APP_ANALYTICS_API}",
  REACT_APP_LLM_API: "${REACT_APP_LLM_API}",
  REACT_APP_ENV: "${REACT_APP_ENV}"
};
EOF

echo "Starting nginx..."
exec "$@"