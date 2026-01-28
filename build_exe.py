import PyInstaller.__main__
import os
import sys

def build():
    print("Building PlayGet...")
    
    # Check for required files
    required = ['ffmpeg.exe', 'ffprobe.exe']
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print(f"Error: Missing required files: {missing}")
        return

    icon_path = 'icon.png' if os.path.exists('icon.png') else None
    
    args = [
        'app_gui.py',
        '--name=PlayGet',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
        '--add-binary=ffmpeg.exe;.',
        '--add-binary=ffprobe.exe;.',
        '--hidden-import=yt_dlp',
    ]

    if icon_path:
        args.append(f'--icon={icon_path}')
        args.append(f'--add-data={icon_path};.')
        print(f"Using icon: {icon_path}")

    print(f"Running PyInstaller with args: {args}")
    PyInstaller.__main__.run(args)
    print("Build complete! executable is in 'dist' folder.")

if __name__ == "__main__":
    build()
