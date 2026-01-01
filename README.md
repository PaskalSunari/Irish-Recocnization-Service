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

---------------Routing endpoint in the api---------------
------192.168.1.21 ip where the service is installed---------
**User list**
http://192.168.1.21:5001/ 
**Camera**
http://192.168.1.21:5001/Camera
**Camera Control**
http://192.168.1.21:5001/CameraControl
**Slave Mode**
http://192.168.1.21:5001/SlaveMode
**Recocnize Mode**
http://192.168.1.21:5001/RecogMode
**Start Camera**
http://192.168.1.21:5001/StartCamera
**Stop Camera**
http://192.168.1.21:5001/StopCamera
**Match Data**
http://192.168.1.21:5001/MatchData
**Last User in the List**
http://192.168.1.21:5001/LastUserDetail
**Live Face Preview**
http://192.168.1.21:5001/LivePreview


---------------Environment Create-----------------------------------------
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt


---------------Building installer service--------------------------

 
1. pip install pyinstaller
2. pyinstaller main.spec
3. Install Inno Setup (if not already installed)
4. Open Inno Setup Compiler
5. Open Your setup.iss Script & compile
6. When finished, it will show you the output folder & application is built in installer folder
