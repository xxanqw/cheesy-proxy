from os import system, path, walk
import requests
import tarfile
import colorama
from zipfile import ZipFile

#Info
version = "1.0.3.0"

# Initialize colorama
colorama.init()

# Print the banner
system('cls')
print(colorama.Fore.YELLOW + """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡞⠉⠛⠶⢤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⢰⠞⠛⢷⠀⠈⠙⠳⠦⣄⣀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠁⠀⠘⠒⠒⠋⠀⣠⣤⡀⠀⠀⠉⠛⢶⣤⣀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡼⠋⢀⡴⠖⠶⢦⠀⠀⠀⢧⣬⠇⣀⣠⠴⠞⠋⠁⡏
⠀⠀⠀⠀⠀⠀⠀⠀⣠⠟⠀⠀⠘⠧⣤⣀⡼⠀⢀⣀⡤⠶⢛⣩⣤⣀⠀⢠⡞⠋
⠀⠀⠀⠀⠀⠀⣠⠞⣁⣀⠀⠀⠀⠀⢀⣠⡴⠖⠋⠁⠀⠀⣿⠁⠀⣹⠀⠈⢷⡄
⠀⠀⠀⠀⣠⠞⠁⠀⠷⠿⣀⣤⠴⠚⠉⠁⠀⠀⠀⠀⠀⠀⠈⠓⠒⠃⠀⠀⠀⡇
⠀⠀⣠⠞⣁⣠⡤⠶⠚⠛⠉⠀⠀⠀⣀⡀⠀⠀⠀⠀⢀⡤⠶⠶⠦⣄⠀⠀⠀⡇
⠀⡾⠛⠋⢉⣤⢤⣀⠀⠀⠀⠀⣰⠞⠉⠙⠳⡄⠀⠀⡟⠀⠀⠀⠀⢸⡆⠀⠀⡇
⠀⡇⠀⢰⡏⠀⠀⢹⡆⠀⠀⠀⡇⠀⠀⠀⠀⣿⠀⠀⠳⣄⡀⠀⢀⣸⠇⠀⠀⡇
⠀⡇⠀⠀⢷⣤⣤⠞⠁⠀⠀⠀⢷⣀⣀⣠⡴⠃⠀⠀⠀⠈⠉⠉⠉⠁⣀⣠⠴⠇
⠀⠻⣆⠀⠀⠀⠀⢀⣀⣤⣀⠀⠀⠉⠉⠁⠀⠀⠀⠀⠀⢀⣠⡤⠖⠛⠉⠀⠀⠀
⠀⠀⡿⠀⠀⠀⢰⡏⠀⠀⢹⡆⠀⠀⠀⠀⠀⣀⣤⠶⠚⠉⠁⠀⠀⠀⠀⠀⠀⠀
⢰⠞⠁⠀⠀⠀⠀⢷⣄⣤⠞⠁⣀⣠⠴⠚⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⡆⠀⠀⠀⠀⠀⠀⣀⡤⠖⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⡇⠀⢀⣠⡴⠞⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
""")
print(colorama.Fore.WHITE + f"Cheesy Proxy Builder ({version})\n")

print(colorama.Fore.WHITE + "Downloading wireproxy...")
try:
    url = "https://github.com/pufferffish/wireproxy/releases/latest/download/wireproxy_windows_amd64.tar.gz"
    response = requests.get(url)
    with open("wireproxy_windows_amd64.tar.gz", "wb") as file:
        file.write(response.content)
    print(colorama.Fore.GREEN + "Done!")
except Exception as e:
    print(colorama.Fore.RED + f"Failed to download wireproxy.\nError: {e}")
    exit(1)

print(colorama.Fore.WHITE + "\nExtracting wireproxy...")
filename = "wireproxy.exe"
try:
    with tarfile.open("wireproxy_windows_amd64.tar.gz", "r") as tar:
        tar.extract(member=filename, filter=lambda x, _: x if x.name == filename else None)
    print(colorama.Fore.GREEN + "Done!")
except Exception as e:
    print(colorama.Fore.RED + f"Failed to extract wireproxy.\nError: {e}")
    exit(1)

print(colorama.Fore.WHITE + "\nBuilding...")
try:
    system(f'python -m nuitka --standalone --windows-icon-from-ico=icons/icon.png --include-data-dir=icons=icons --include-data-files=wireproxy.exe=wireproxy.exe --windows-console-mode=disable --enable-plugin=pyqt6  --product-name="cheesy proxy" --product-version={version} --file-description="Cheesy Proxy" --copyright="©️2024 xxanqw" -o "cheesy proxy" main.py')
    print(colorama.Fore.GREEN + "Done!")
except Exception as e:
    print(colorama.Fore.RED + f"Failed to build.\nError: {e}")
    exit(1)

print(colorama.Fore.WHITE + "\nCreating portable...")
try:
    with ZipFile("cheesyproxy_portable.zip", "w") as zip:
        for root, _, files in walk("main.dist"):
            for file in files:
                zip.write(path.join(root, file), path.join("cheesy proxy", path.relpath(path.join(root, file), "main.dist")))
    print(colorama.Fore.GREEN + "Done!")
except Exception as e:
    print(colorama.Fore.RED + f"Failed to create portable.\nError: {e}")
    exit(1)

print(colorama.Fore.WHITE + "\nCleaning up...")
try:
    system('del wireproxy.exe')
    system('del wireproxy_windows_amd64.tar.gz')
    system('rmdir /s /q main.dist')
    system('rmdir /s /q main.build')
    print(colorama.Fore.GREEN + "Done!")
except Exception as e:
    print(colorama.Fore.RED + f"Failed to clean up.\nError: {e}")
    exit(1)

print(colorama.Fore.GREEN + "\nBuild successful!")