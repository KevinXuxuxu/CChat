import curses
import curses.textpad

class CurseLines:
    def __init__(self, window):
        self.lines = []
        self.window = window
        self.height, self.width = window.getmaxyx()
    def push(self, line):
        self.lines.append(line)
        newlines = reversed(self.lines[-(self.height-1):])
        self.window.clear()
        for line in newlines:
            self.window.addstr(line)
        self.window.refresh()
def cur(screen):
    curses.noecho()
    screen.keypad(1)
    height, width = screen.getmaxyx()
    screen.addstr(height-3, 0, '------------------------------------')
    screen.refresh()
    display = screen.subwin(height-3, width-1, 0, 0)
    textarea = screen.subwin(height-2, 0)
    textarea.addstr("This is subwin")
    textbox = curses.textpad.Textbox(textarea)
    lines = CurseLines(display)
    while True:
        line = textbox.edit()
        if line == 'quit':
            break
        else:
            lines.push(line)
    curses.endwin()


if __name__ == '__main__':
    curses.wrapper(cur)
