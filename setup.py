"""
Setup script for building Pomodoro.app with py2app.

Usage:
    uv run python setup.py py2app
"""

from setuptools import setup

APP = ['pomodoro.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,  # Add path to .icns file if you have one
    'plist': {
        'CFBundleName': 'Pomodoro',
        'CFBundleDisplayName': 'Pomodoro Timer',
        'CFBundleIdentifier': 'com.pomodoro.timer',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # Hide from Dock (menu bar app)
        'NSHumanReadableCopyright': 'MIT License',
    },
    'packages': ['rumps'],
    'includes': [
        'Quartz',
        'Quartz.CoreGraphics',
    ],
}

setup(
    app=APP,
    name='Pomodoro',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
