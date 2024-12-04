"""Build script for creating executable."""
import PyInstaller.__main__
import os
import shutil
import sys
import site
import customtkinter

def build_executable():
    """Build the executable using PyInstaller."""
    # Clean previous builds
    for dir_name in ['dist', 'build']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Get customtkinter path
    customtkinter_path = os.path.dirname(customtkinter.__file__)
    
    # Configure PyInstaller
    PyInstaller.__main__.run([
        'src/main.py',
        '--name=BotManager',
        '--windowed',
        '--onefile',
        '--clean',
        '--noconfirm',
        '--hidden-import=customtkinter',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=playwright',
        f'--add-data={customtkinter_path}{os.pathsep}customtkinter',
        '--add-data=src/assets;assets',
        '--add-data=src/config;config',
        '--add-data=src/utils;utils',
        '--add-data=src/bot;bot',
        '--add-data=src/gui;gui',
        '--icon=src/assets/icon.ico'
    ])

if __name__ == "__main__":
    build_executable()