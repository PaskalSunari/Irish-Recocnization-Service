## Proxy Configuration

For local frontend development, use the following proxy configuration (e.g., in `proxy.conf.json`):

{
  "/api/air": {
    "target": "http://server.com:52774",
    "secure": false,
    "changeOrigin": true
  }
}

This allows API requests to `/api/air` to be forwarded to your backend server.