import os
import sys
import tarfile
import shutil
import requests
import colorama
from zipfile import ZipFile, ZIP_DEFLATED
from os.path import abspath, dirname, join, relpath, exists

# Initialize colorama
colorama.init(autoreset=True)

# Constants
VERSION = "1.0.4"
WIREPROXY_URL = "https://github.com/pufferffish/wireproxy/releases/latest/download/wireproxy_windows_amd64.tar.gz"
WIREPROXY_ARCHIVE = "wireproxy_windows_amd64.tar.gz"
WIREPROXY_EXE = "wireproxy.exe"
BUILD_OUTPUT = "cheesy proxy"
DIST_DIR = "main.dist"
PORTABLE_ZIP = "cheesyproxy_portable.zip"
I18N_DIR = "i18n"

def clear_console():
    os.system('cls')

def print_banner():
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
    print(colorama.Fore.WHITE + f"Cheesy Proxy Builder ({VERSION})\n")

def download_wireproxy():
    print(colorama.Fore.WHITE + "Downloading wireproxy...")
    if not exists(WIREPROXY_ARCHIVE):
        try:
            response = requests.get(WIREPROXY_URL, stream=True)
            response.raise_for_status()
            with open(WIREPROXY_ARCHIVE, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(colorama.Fore.GREEN + "Download completed!")
        except requests.RequestException as e:
            print(colorama.Fore.RED + f"Failed to download wireproxy. Error: {e}")
            sys.exit(1)
    else:
        print(colorama.Fore.YELLOW + "Wireproxy already downloaded. Skipping...")

def extract_wireproxy():
    print(colorama.Fore.WHITE + "\nExtracting wireproxy...")
    if not exists(WIREPROXY_EXE):
        try:
            with tarfile.open(WIREPROXY_ARCHIVE, "r:gz") as tar:
                tar.extract(WIREPROXY_EXE)
            print(colorama.Fore.GREEN + "Extraction completed!")
        except (tarfile.TarError, FileNotFoundError) as e:
            print(colorama.Fore.RED + f"Failed to extract wireproxy. Error: {e}")
            sys.exit(1)
    else:
        print(colorama.Fore.YELLOW + "Wireproxy already extracted. Skipping...")

def build_project():
    print(colorama.Fore.WHITE + "\nBuilding project...")
    build_command = (
        f'python -m nuitka --standalone --windows-icon-from-ico=icons/icon.png '
        f'--include-data-dir=icons=icons --include-data-files={WIREPROXY_EXE}={WIREPROXY_EXE} '
        f'--include-data-dir={I18N_DIR}={I18N_DIR} '
        f'--windows-console-mode=disable --enable-plugin=pyside6 '
        f'--product-name="cheesy proxy" --product-version={VERSION} '
        f'--file-description="Cheesy Proxy" --copyright="©️2024 xxanqw" '
        f'--output-filename="{BUILD_OUTPUT}" main.py'
    )
    try:
        result = os.system(build_command)
        if result != 0:
            raise Exception("Build command failed")
        print(colorama.Fore.GREEN + "Build completed!")
    except Exception as e:
        print(colorama.Fore.RED + f"Failed to build project. Error: {e}")
        sys.exit(1)

def create_portable_zip():
    print(colorama.Fore.WHITE + "\nCreating portable ZIP...")
    try:
        with ZipFile(PORTABLE_ZIP, "w", compression=ZIP_DEFLATED, compresslevel=9) as zip_file:
            for root, _, files in os.walk(DIST_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join(BUILD_OUTPUT, os.path.relpath(file_path, DIST_DIR))
                    zip_file.write(file_path, arcname)
        print(colorama.Fore.GREEN + "Portable ZIP created!")
    except Exception as e:
        print(colorama.Fore.RED + f"Failed to create portable ZIP. Error: {e}")
        sys.exit(1)

def cleanup():
    print(colorama.Fore.WHITE + "\nCleaning up...")
    try:
        if exists(WIREPROXY_EXE):
            os.remove(WIREPROXY_EXE)
        if exists(WIREPROXY_ARCHIVE):
            os.remove(WIREPROXY_ARCHIVE)
        if exists("main.build"):
            shutil.rmtree("main.build")
        print(colorama.Fore.GREEN + "Cleanup completed!")
    except Exception as e:
        print(colorama.Fore.RED + f"Failed to clean up. Error: {e}")
        sys.exit(1)

def main():
    clear_console()
    print_banner()
    download_wireproxy()
    extract_wireproxy()
    build_project()
    create_portable_zip()
    cleanup()
    print(colorama.Fore.GREEN + "\nBuild successful!")

if __name__ == "__main__":
    main()