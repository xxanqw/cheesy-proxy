# cheesy proxy
Simple, lightweight and easy to use wireproxy client

## Usage
>[!IMPORTANT]  
>You need to download wireproxy.exe by yourself, you can find repository down below in `Thanks` section.  
>Same with config file, you need to have your own server with WireGuard installation. Same can be found down below.   
>You may face some bugs (it's a WIP project, but still usable)

- Download latest release and install it
- After launching choose paths to wireproxy and your WireGuard config file  
  Make sure that your config file has this lines:  
  ```
  [Socks5]
  BindAddress = 127.0.0.1:25344
  ```
  You can use any port you like tho  
  And press `Save`
- Right click cheese icon in your tray and press `Start`
- You're good to go proxy is up running you can connect to it with your browser extensions and other proxy utilities!

## Build
>[!NOTE]  
>Do not build it as onefile, code is not optimized for this

Just copy this and paste into your terminal (Use PowerShell)
```
git clone https://github.com/xxanqw/cheesy-proxy
cd cheesy-proxy
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements
python build.py
```

## Thanks
to [wireproxy](https://github.com/pufferffish/wireproxy) and [wireguard-install](https://github.com/hwdsl2/wireguard-install)