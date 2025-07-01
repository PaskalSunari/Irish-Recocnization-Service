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

---------------------------------Rout Path in the api---------------------------------------------
**User list**
http://192.168.1.12:5001/
**Camera**
http://192.168.1.12:5001/Camera
**Camera Control**
http://192.168.1.12:5001/CameraControl
**Slave Mode**
http://192.168.1.12:5001/SlaveMode
**Recocnize Mode**
http://192.168.1.12:5001/RecogMode
**Start Camera**
http://192.168.1.12:5001/StartCamera
**Stop Camera**
http://192.168.1.12:5001/StartCamera
**Match Data**
http://192.168.1.12:5001/MatchData
