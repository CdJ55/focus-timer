import time
import os
import sys
import json
from datetime import date, datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sessions.json')

WORK_MINUTES    = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN  = 15
POMODOROS_BEFORE_LONG = 4

# ANSI colors (disabled on old Windows consoles)
def _ansi(code): return f'\033[{code}m'
try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleMode(
        ctypes.windll.kernel32.GetStdHandle(-11), 7)
    COLORS = True
except Exception:
    COLORS = os.name != 'nt'

RED    = _ansi('31') if COLORS else ''
GREEN  = _ansi('32') if COLORS else ''
YELLOW = _ansi('33') if COLORS else ''
CYAN   = _ansi('36') if COLORS else ''
BOLD   = _ansi('1')  if COLORS else ''
DIM    = _ansi('2')  if COLORS else ''
RESET  = _ansi('0')  if COLORS else ''

DIGITS = {
    '0': [' ___ ', '|   |', '|   |', '|   |', '|___|'],
    '1': ['  |  ', '  |  ', '  |  ', '  |  ', '  |  '],
    '2': [' ___ ', '    |', ' ___ ', '|    ', '|___ '],
    '3': [' ___ ', '    |', ' ___ ', '    |', ' ___ '],
    '4': ['|   |', '|___|', '    |', '    |', '    |'],
    '5': [' ___ ', '|    ', '|___ ', '    |', '|___|'],
    '6': [' ___ ', '|    ', '|___ ', '|   |', '|___|'],
    '7': [' ___ ', '    |', '    |', '    |', '    |'],
    '8': [' ___ ', '|   |', '|___|', '|   |', '|___|'],
    '9': [' ___ ', '|   |', '|___|', '    |', '|___|'],
    ':': ['     ', '  *  ', '     ', '  *  ', '     '],
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_time(minutes, seconds, color=''):
    s = f'{minutes:02d}:{seconds:02d}'
    rows = [''] * 5
    for ch in s:
        d = DIGITS.get(ch, DIGITS['0'])
        for i in range(5):
            rows[i] += d[i] + '  '
    return '\n'.join(f'  {color}{row}{RESET}' for row in rows)

def progress_bar(elapsed, total, width=38):
    filled = int(width * elapsed / total) if total else 0
    filled = min(filled, width)
    bar = '#' * filled + '-' * (width - filled)
    pct = int(100 * elapsed / total) if total else 0
    return f'  [{GREEN}{bar}{RESET}] {pct:3d}%'

def ding():
    print('\a', end='', flush=True)

# ── Data persistence ────────────────────────────────────────────────────────

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {'sessions': [], 'streak': 0, 'last_date': None}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def count_today(data):
    today = str(date.today())
    return sum(1 for s in data['sessions']
               if s.get('date') == today and s.get('type') == 'work')

def update_streak(data):
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    last = data.get('last_date')
    if last == today:
        return
    data['streak'] = (data.get('streak', 0) + 1) if last == yesterday else 1
    data['last_date'] = today

# ── Splash ──────────────────────────────────────────────────────────────────

def splash(data):
    clear()
    today_count = count_today(data)
    streak = data.get('streak', 0)
    flame = '*' if streak >= 3 else ' '
    print(f'\n  {BOLD}{CYAN}FOCUS TIMER{RESET}  {YELLOW}{flame} {streak}-day streak{RESET}')
    print(f'  {DIM}Pomodoro technique: 25 min focus / 5 min break{RESET}')
    print(f'  {DIM}{"─"*40}{RESET}')
    if today_count:
        dots = (GREEN + 'o' + RESET) * today_count
        print(f'  Today: {dots}  ({today_count} pomodoro{"s" if today_count != 1 else ""} done)')
    else:
        print(f'  {DIM}No pomodoros yet today — let\'s get started!{RESET}')
    print()

# ── Timer loop ───────────────────────────────────────────────────────────────

def run_timer(label, total_seconds, data, color):
    start = time.time()
    try:
        while True:
            elapsed = time.time() - start
            remaining = max(0.0, total_seconds - elapsed)
            m = int(remaining) // 60
            s = int(remaining) % 60

            clear()
            today_count = count_today(data)
            streak = data.get('streak', 0)

            print(f'\n  {BOLD}{color}{label}{RESET}')
            print(f'  {DIM}{"─"*40}{RESET}\n')
            print(render_time(m, s, color))
            print()
            print(progress_bar(elapsed, total_seconds))
            print()
            print(f'  {DIM}Today: {today_count} done  |  Streak: {streak} day{"s" if streak != 1 else ""}{RESET}')
            print(f'  {DIM}Ctrl+C to skip{RESET}')

            if remaining <= 0:
                ding()
                return True
            time.sleep(0.5)
    except KeyboardInterrupt:
        return False

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    data = load_data()
    update_streak(data)
    save_data(data)

    splash(data)
    print(f'  Press {BOLD}Enter{RESET} to start your first pomodoro, or {BOLD}Ctrl+C{RESET} to quit.\n')
    try:
        input()
    except KeyboardInterrupt:
        print('\n  Bye!\n')
        return

    pomodoro_in_cycle = 0

    while True:
        num = count_today(data) + 1
        completed = run_timer(
            f'FOCUS  —  Pomodoro #{num}',
            WORK_MINUTES * 60,
            data,
            CYAN,
        )

        if completed:
            data['sessions'].append({
                'date': str(date.today()),
                'time': datetime.now().strftime('%H:%M'),
                'type': 'work',
            })
            update_streak(data)
            save_data(data)
            pomodoro_in_cycle += 1

            clear()
            today_count = count_today(data)
            streak = data.get('streak', 0)
            dots = (GREEN + 'o' + RESET) * today_count
            print(f'\n  {GREEN}{BOLD}Pomodoro #{today_count} done!{RESET}  {dots}')
            print(f'  Streak: {YELLOW}{streak} day{"s" if streak != 1 else ""}{RESET}\n')
        else:
            clear()
            print(f'\n  {DIM}Session skipped.{RESET}\n')

        if pomodoro_in_cycle >= POMODOROS_BEFORE_LONG:
            break_label  = 'LONG BREAK'
            break_secs   = LONG_BREAK_MIN * 60
            pomodoro_in_cycle = 0
        else:
            break_label = 'SHORT BREAK'
            break_secs  = SHORT_BREAK_MIN * 60

        mins = break_secs // 60
        print(f'  Press {BOLD}Enter{RESET} for a {mins}-min {break_label}, '
              f'or {BOLD}Ctrl+C{RESET} to quit.\n')
        try:
            input()
        except KeyboardInterrupt:
            print(f'\n  {DIM}Good work today. Bye!{RESET}\n')
            break

        run_timer(break_label, break_secs, data, GREEN)

        clear()
        print(f'\n  {GREEN}Break over!{RESET}\n')
        print(f'  Press {BOLD}Enter{RESET} for the next pomodoro, '
              f'or {BOLD}Ctrl+C{RESET} to stop.\n')
        try:
            input()
        except KeyboardInterrupt:
            print(f'\n  {DIM}See you next time!{RESET}\n')
            break

if __name__ == '__main__':
    main()
