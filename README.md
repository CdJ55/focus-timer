# Focus Timer

A terminal Pomodoro timer with a big ASCII clock, color output, and session tracking.

## Features

- 25-minute focus blocks with 5-minute short breaks and 15-minute long breaks
- Large ASCII digit countdown display
- Progress bar and percentage
- Daily pomodoro count and streak tracking (saved to `sessions.json`)
- Works on Windows, macOS, and Linux

## Usage

```bash
python timer.py
```

Press **Enter** to start a session, **Ctrl+C** to skip or quit.

## Configuration

Edit the constants at the top of `timer.py`:

| Variable               | Default | Description                        |
|------------------------|---------|------------------------------------|
| `WORK_MINUTES`         | 25      | Length of each focus block         |
| `SHORT_BREAK_MIN`      | 5       | Short break after each pomodoro    |
| `LONG_BREAK_MIN`       | 15      | Long break every 4 pomodoros       |
| `POMODOROS_BEFORE_LONG`| 4       | Pomodoros per cycle before long break |

## Requirements

Python 3.6+ — no third-party packages needed.
