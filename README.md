# Pomodoro Timer for macOS

A simple, native menu bar Pomodoro timer app for macOS to help you stay focused and productive.

![Pomodoro Timer](https://img.shields.io/badge/macOS-Menu%20Bar%20App-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)

## Features

- **Menu Bar Integration** - Lives in your macOS menu bar, always accessible
- **Pomodoro Technique** - 25-minute focus sessions with short and long breaks
- **Smart Break Scheduling** - Short breaks (5 min) after each session, long breaks (15 min) after every 4 sessions
- **Activity Detection** - Automatically detects when you're ready to start the next session
- **Session Tracking** - Tracks your completed focus sessions for the day
- **Inspirational Quotes** - Displays motivational messages about focus and productivity
- **Start at Login** - Optional auto-start when you log in to your Mac
- **Native Notifications** - macOS notifications to keep you on track

## Quick Install

1. Download `Pomodoro.app` from this repository (or `dist/Pomodoro.zip`)
2. Move it to your Applications folder
3. Double-click to run
4. If prompted about an unidentified developer, right-click the app and select "Open"

## Usage

- Click the tomato icon (🍅) in your menu bar
- Select **Start Focus** to begin a 25-minute focus session
- The timer shows in the menu bar: `🍅 24:59` during focus, `☕ 04:59` during breaks
- After focus ends, a break starts automatically
- After the break, move your mouse or press a key to start the next focus session
- Use **Skip to Rest** to end a focus session early
- Use **Stop Timer** to cancel and return to idle state

## Building from Source

### Requirements

- Python 3.x
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/misrasaurabh1/pomodoro-mac.git
cd pomodoro-mac

# Install dependencies
uv sync

# Run from source
uv run python pomodoro.py
```

### Build the App

```bash
# Install PyInstaller
uv pip install pyinstaller

# Build the .app bundle
pyinstaller Pomodoro.spec
```

The built app will be in `dist/Pomodoro.app`.

## Configuration

Default timer durations:
- Focus: 25 minutes
- Short Break: 5 minutes
- Long Break: 15 minutes
- Sessions until long break: 4

## License

Apache License 2.0

## Author

Created by Saurabh Misra
