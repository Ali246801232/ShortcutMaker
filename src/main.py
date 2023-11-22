import shortcuts
from terminal import setup_terminal, start_terminal, hide_terminal



# Read existing shortcuts from shortcuts file
def read_file():
    with open(shortcuts.SHORTCUTS_FILE, 'r') as file:
        line_num = 0
        for line in file:
            line = line.strip()
            line_num += 1
            if not line:
                continue
            try:
                shortcut = shortcuts.validate_shortcut(line)
            except Exception as e:
                print(f"{e} (Line {line_num})")
                return False
            try:
                shortcuts.SHORTCUTS[shortcut.sequence.name] = shortcut
            except KeyError:
                raise ValueError(f"Error: Sequence name {shortcut.sequence.name} already used")
    for shortcut in shortcuts. SHORTCUTS.values():
        shortcut.assign()

def main():
    try:
        read_file()
        setup_terminal()
        hide_terminal()
        start_terminal()
    except Exception as e:
        print(e)



if __name__ == "__main__":
    main()
