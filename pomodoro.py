#!/usr/bin/env python3
"""
Pomodoro Timer for macOS
A menu bar app for focus and productivity.
"""

import rumps
import threading
import time
import random
import os
import sys
import plistlib
from pathlib import Path
from enum import Enum
from Quartz.CoreGraphics import CGEventSourceSecondsSinceLastEventType, kCGEventSourceStateCombinedSessionState


APP_NAME = "Pomodoro"
APP_VERSION = "1.1.0"
APP_AUTHOR = "Saurabh Misra"
BUNDLE_ID = "com.saurabhmisra.pomodoro"


def get_launch_agent_path():
    """Get the path to the LaunchAgent plist file."""
    return Path.home() / "Library" / "LaunchAgents" / f"{BUNDLE_ID}.plist"


def get_app_executable():
    """Get the path to the app executable."""
    if getattr(sys, 'frozen', False):
        # Running as bundled app
        return sys.executable
    else:
        # Running as script
        return os.path.abspath(__file__)


def is_autostart_enabled():
    """Check if auto-start on login is enabled."""
    return get_launch_agent_path().exists()


def enable_autostart():
    """Enable auto-start on login by creating a LaunchAgent."""
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)

    executable = get_app_executable()

    # Build the program arguments based on how we're running
    if getattr(sys, 'frozen', False):
        # Bundled .app - use open command
        app_path = str(Path(executable).parent.parent.parent)  # Go up from MacOS/executable to .app
        program_args = ["/usr/bin/open", app_path]
    else:
        # Running as script - use Python
        program_args = [sys.executable, executable]

    plist_content = {
        "Label": BUNDLE_ID,
        "ProgramArguments": program_args,
        "RunAtLoad": True,
        "KeepAlive": False,
    }

    plist_path = get_launch_agent_path()
    with open(plist_path, "wb") as f:
        plistlib.dump(plist_content, f)

    # Load the agent
    os.system(f"launchctl load {plist_path}")


def disable_autostart():
    """Disable auto-start on login by removing the LaunchAgent."""
    plist_path = get_launch_agent_path()
    if plist_path.exists():
        # Unload the agent first
        os.system(f"launchctl unload {plist_path}")
        plist_path.unlink()


class TimerState(Enum):
    IDLE = "idle"
    FOCUS = "focus"
    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    WAITING_FOR_USER = "waiting"


# Inspirational messages about focus
INSPIRATIONAL_MESSAGES = [
    "Deep work is the superpower of the 21st century. - Cal Newport",
    "Focus is saying no to 1,000 other things. - Steve Jobs",
    "The successful warrior is the average man with laser-like focus. - Bruce Lee",
    "Concentrate all your thoughts upon the work at hand. - Alexander Graham Bell",
    "Where focus goes, energy flows. - Tony Robbins",
    "The ability to concentrate is a skill that gets valuable things done.",
    "Single-tasking is the new superpower in a world of distractions.",
    "Your focus determines your reality. - George Lucas",
    "Lack of direction, not lack of time, is the problem. - Zig Ziglar",
    "Focus on being productive instead of busy. - Tim Ferriss",
    "The shorter way to do many things is to do only one thing at a time.",
    "Starve your distractions, feed your focus.",
    "Focus is a matter of deciding what things you're not going to do. - John Carmack",
    "Multitasking is the enemy of focus and excellence.",
    "25 minutes of deep focus beats 2 hours of scattered attention.",
]


class PomodoroApp(rumps.App):
    def __init__(self):
        super().__init__("🍅 Ready", quit_button=None)

        # Timer settings (in seconds)
        self.focus_duration = 25 * 60
        self.short_rest_duration = 5 * 60
        self.long_rest_duration = 15 * 60
        self.sessions_until_long_rest = 4

        # State
        self.state = TimerState.IDLE
        self.time_remaining = 0
        self.completed_sessions = 0
        self.sessions_today = 0
        self.timer_thread = None
        self.running = False

        # Build menu
        self.start_button = rumps.MenuItem("Start Focus", callback=self.start_focus)
        self.skip_button = rumps.MenuItem("Skip to Rest", callback=self.skip_to_rest)
        self.skip_button.set_callback(None)  # Disabled initially
        self.stop_button = rumps.MenuItem("Stop Timer", callback=self.stop_timer)
        self.stop_button.set_callback(None)  # Disabled initially

        self.stats_item = rumps.MenuItem(f"Sessions today: {self.sessions_today}")
        self.stats_item.set_callback(None)  # Not clickable

        # Settings submenu
        self.settings_menu = rumps.MenuItem("Settings")
        self.focus_setting = rumps.MenuItem(f"Focus: {self.focus_duration // 60} min")
        self.short_rest_setting = rumps.MenuItem(f"Short Rest: {self.short_rest_duration // 60} min")
        self.long_rest_setting = rumps.MenuItem(f"Long Rest: {self.long_rest_duration // 60} min")

        # Auto-start toggle
        self.autostart_item = rumps.MenuItem(
            "Start at Login",
            callback=self.toggle_autostart
        )
        self.autostart_item.state = is_autostart_enabled()

        self.settings_menu.update([
            self.focus_setting,
            self.short_rest_setting,
            self.long_rest_setting,
            None,  # Separator
            self.autostart_item,
        ])

        # About submenu
        self.about_menu = rumps.MenuItem("About")
        self.about_name = rumps.MenuItem(f"{APP_NAME} v{APP_VERSION}")
        self.about_name.set_callback(None)
        self.about_author = rumps.MenuItem(f"Created by {APP_AUTHOR}")
        self.about_author.set_callback(None)
        self.about_menu.update([
            self.about_name,
            self.about_author,
        ])

        self.menu = [
            self.start_button,
            self.skip_button,
            self.stop_button,
            None,  # Separator
            self.stats_item,
            None,  # Separator
            self.settings_menu,
            self.about_menu,
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]

    def get_idle_time(self):
        """Get system idle time in seconds using Quartz."""
        return CGEventSourceSecondsSinceLastEventType(
            kCGEventSourceStateCombinedSessionState,
            0xFFFFFFFF  # All event types
        )

    def format_time(self, seconds):
        """Format seconds as MM:SS."""
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02d}:{secs:02d}"

    def update_title(self):
        """Update menu bar title with current state and time."""
        if self.state == TimerState.IDLE:
            self.title = "🍅 Ready"
        elif self.state == TimerState.FOCUS:
            self.title = f"🍅 {self.format_time(self.time_remaining)}"
        elif self.state in (TimerState.SHORT_REST, TimerState.LONG_REST):
            self.title = f"☕ {self.format_time(self.time_remaining)}"
        elif self.state == TimerState.WAITING_FOR_USER:
            self.title = "🍅 Waiting..."

    def update_menu_state(self):
        """Update menu items based on current state."""
        if self.state == TimerState.IDLE:
            self.start_button.set_callback(self.start_focus)
            self.skip_button.title = "Skip to Rest"
            self.skip_button.set_callback(None)
            self.stop_button.set_callback(None)
        elif self.state == TimerState.FOCUS:
            self.start_button.set_callback(None)
            self.skip_button.title = "Skip to Rest"
            self.skip_button.set_callback(self.skip_to_rest)
            self.stop_button.set_callback(self.stop_timer)
        elif self.state in (TimerState.SHORT_REST, TimerState.LONG_REST):
            self.start_button.set_callback(None)
            self.skip_button.title = "Skip to Focus"
            self.skip_button.set_callback(self.skip_to_focus)
            self.stop_button.set_callback(self.stop_timer)
        elif self.state == TimerState.WAITING_FOR_USER:
            self.start_button.set_callback(self.start_focus)
            self.skip_button.title = "Skip to Rest"
            self.skip_button.set_callback(None)
            self.stop_button.set_callback(self.stop_timer)

        self.stats_item.title = f"Sessions today: {self.sessions_today}"

    def get_random_message(self):
        """Get a random inspirational message."""
        return random.choice(INSPIRATIONAL_MESSAGES)

    def notify(self, title, message, sound=True):
        """Send a notification."""
        rumps.notification(
            title=title,
            subtitle="",
            message=message,
            sound=sound
        )

    def start_focus(self, _=None):
        """Start a focus session."""
        self.state = TimerState.FOCUS
        self.time_remaining = self.focus_duration
        self.running = True
        self.update_title()
        self.update_menu_state()

        self.notify(
            "Focus Time! 🎯",
            f"{self.focus_duration // 60} minutes of deep work. {self.get_random_message()}"
        )

        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()

    def start_rest(self, is_long=False):
        """Start a rest period."""
        if is_long:
            self.state = TimerState.LONG_REST
            self.time_remaining = self.long_rest_duration
            rest_type = "Long Break"
            duration = self.long_rest_duration // 60
        else:
            self.state = TimerState.SHORT_REST
            self.time_remaining = self.short_rest_duration
            rest_type = "Short Break"
            duration = self.short_rest_duration // 60

        self.running = True
        self.update_title()
        self.update_menu_state()

        self.notify(
            f"{rest_type}! ☕",
            f"Take {duration} minutes to relax. You've earned it!"
        )

    def skip_to_rest(self, _=None):
        """Skip current focus session to rest."""
        if self.state == TimerState.FOCUS:
            is_long = (self.completed_sessions + 1) % self.sessions_until_long_rest == 0
            self.start_rest(is_long=is_long)

    def skip_to_focus(self, _=None):
        """Skip current rest session to focus."""
        if self.state in (TimerState.SHORT_REST, TimerState.LONG_REST):
            self.start_focus()

    def stop_timer(self, _=None):
        """Stop the timer and return to idle."""
        self.running = False
        self.state = TimerState.IDLE
        self.time_remaining = 0
        self.update_title()
        self.update_menu_state()

    def wait_for_user(self):
        """Wait for user activity before starting next focus session."""
        self.state = TimerState.WAITING_FOR_USER
        self.update_title()
        self.update_menu_state()

        self.notify(
            "Ready to focus? 🍅",
            "Move your mouse or press a key to start the next focus session."
        )

        # Poll for user activity
        while self.running and self.state == TimerState.WAITING_FOR_USER:
            idle_time = self.get_idle_time()
            if idle_time < 3:  # User active in last 3 seconds
                self.start_focus()
                return
            time.sleep(1)

    def timer_loop(self):
        """Main timer loop running in a separate thread."""
        while self.running:
            if self.state in (TimerState.FOCUS, TimerState.SHORT_REST, TimerState.LONG_REST):
                if self.time_remaining > 0:
                    time.sleep(1)
                    self.time_remaining -= 1
                    self.update_title()
                else:
                    # Timer finished
                    if self.state == TimerState.FOCUS:
                        self.completed_sessions += 1
                        self.sessions_today += 1
                        self.update_menu_state()

                        # Determine if long rest
                        is_long = self.completed_sessions % self.sessions_until_long_rest == 0
                        self.start_rest(is_long=is_long)

                    elif self.state in (TimerState.SHORT_REST, TimerState.LONG_REST):
                        # Rest finished, wait for user
                        self.wait_for_user()

            elif self.state == TimerState.WAITING_FOR_USER:
                time.sleep(0.5)

            else:
                time.sleep(0.5)

    def toggle_autostart(self, sender):
        """Toggle auto-start on login."""
        if is_autostart_enabled():
            disable_autostart()
            sender.state = False
            self.notify("Auto-start Disabled", "Pomodoro will not start automatically on login.")
        else:
            enable_autostart()
            sender.state = True
            self.notify("Auto-start Enabled", "Pomodoro will start automatically when you log in.")

    def quit_app(self, _=None):
        """Quit the application."""
        self.running = False
        rumps.quit_application()


if __name__ == "__main__":
    app = PomodoroApp()
    app.run()
