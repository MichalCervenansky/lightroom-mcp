import PyInstaller.__main__
import os
import shutil

# Clean up previous builds
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

PyInstaller.__main__.run([
    'start_broker.py',
    '--name=broker',
    '--onefile',
    '--noconsole',  # Hide console window
    '--clean',
    # Add hidden imports if necessary (e.g., flask extensions, pystray backend)
    '--hidden-import=pystray',
    '--hidden-import=PIL',
    '--hidden-import=engineio.async_drivers.threading',
    # Include any data files if needed
    # '--add-data=templates;templates',
])

print("Build complete. Executable is in dist/broker.exe")
