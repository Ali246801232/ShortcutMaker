import re
import keyboard
import pyautogui, win32gui, win32api, win32con
import time

ACTION_TYPES = ["left_click", "right_click", "key_press", "type_string", "wait_time"]  # valid action types
LINE_PATTERN = r'^[^~:;]+:(([^~:;]+)~)*([^~:;]+){1}:[^~:;]+:(([^~:;]+;[^~:;]+;[^~:;]+)~)*([^~:;]+;[^~:;]+;[^~:;]+){1}$'  # valid shortcut/sequence definition pattern

SHORTCUTS = {}  # existing shortcuts
HOTKEYS = {}  # existing hotkeys

SHORTCUTS_FILE = "shortcuts.txt"  # file containing shortcuts

class Action:
    def __init__(self, type, value, hold):
        if type in ACTION_TYPES:
            self.type = type
        else:
            raise ValueError(f"Error: Action type {type} does not exist")

        if self.validate(type, value):
            self.value = value
        else:
            raise ValueError(f"Error: Action value {value} does not match action type {type}")

        if (type in ACTION_TYPES[:4] and (isinstance(hold, (float, int)) and hold >= 0)) or (type == "wait_time" and hold is None):
            self.hold = hold
        else:
            raise ValueError(f"Error: Action hold {hold} is not positive int or float, or None")

    def validate(self, type, value):
        match type:
            case "left_click" | "right_click":
                if isinstance(value, tuple) and all(isinstance(v, int) and v > 0 for v in value):
                    return True
            case "key_press":
                if isinstance(value, str):
                    try:
                        keyboard.key_to_scan_codes(value)
                        return True
                    except ValueError:
                        pass
            case "type_string":
                if isinstance(value, str) and len(value) > 0:
                    return True
            case "wait_time":
                if isinstance(value, (int, float)) and value > 0:
                    return True

        return False

    def perform(self):
        match self.type:
            case "left_click":
                self.left_click()
            case "right_click":
                self.right_click()
            case "key_press":
                self.key_press()
            case "type_string":
                self.type_string()
            case "wait_time":
                self.wait_time()

    def left_click(self):
        original_pos = pyautogui.position()
        original_pos = (original_pos.x, original_pos.y)
        win32api.SetCursorPos(self.value)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, self.value[0], self.value[1], 0, 0)
        time.sleep(self.hold)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, self.value[0], self.value[1], 0, 0)
        win32api.SetCursorPos(original_pos)

    def right_click(self):
        original_pos = pyautogui.position()
        original_pos = (original_pos.x, original_pos.y)
        win32api.SetCursorPos(self.value)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, self.value[0], self.value[1], 0, 0)
        time.sleep(self.hold)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, self.value[0], self.value[1], 0, 0)
        win32api.SetCursorPos(original_pos)

    def key_press(self):
        keyboard.press(self.value)
        time.sleep(self.hold)
        keyboard.release(self.value)

    def type_string(self):
        keyboard.write(self.value, delay=self.hold)

    def wait_time(self):
        time.sleep(self.value)
    
    def __repr__(self):
        value_repr = f'"{self.value}"' if isinstance(self.value, str) else str(self.value)
        return f'Action(type="{self.type}", value={value_repr}, hold={self.hold})'
    
    def __str__(self):
        value_repr = f'"{self.value}"' if isinstance(self.value, str) else str(self.value)
        return f'{self.type};{value_repr};{self.hold}'


class Sequence:
    def __init__(self, name, actions):
        if isinstance(name, str):
            self.name = name
        else:
            raise ValueError(f"Error: Sequence name {name} is not of type string")

        if isinstance(actions, list) and all(isinstance(a, Action) for a in actions):
            self.actions = actions
        else:
            raise ValueError(f"Error: List of actions {actions} is not of type list with items of type Action")

    def execute(self, windows):
        current_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if any(window in current_window for window in windows):
            time.sleep(0.15)
            for action in self.actions:
                action.perform()
    
    def __repr__(self):
        actions_repr = ', '.join([repr(action) for action in self.actions])
        return f'Sequence("{self.name}", [{actions_repr}])'
    
    def __str__(self):
        actions_repr = ' ~ '.join([str(action) for action in self.actions])
        return f'{self.name} : {actions_repr}'

class Shortcut:
    def __init__(self, hotkey, sequence, windows):
        if self.validate(hotkey):
            self.hotkey = hotkey
        else:
            raise ValueError(f"Error: Shortcut {hotkey} is not a valid shortcut")

        if isinstance(sequence, Sequence):
            self.sequence = sequence
        else:
            raise ValueError(f"Error: Assigned sequence {sequence} is not of type Sequence")

        if isinstance(windows, list) and all(isinstance(w, str) for w in windows):
            self.windows = windows
        else:
            raise ValueError(f"Error: List of windows {windows} is not of type list with items of type str")

    def validate(self, hotkey):
        if isinstance(hotkey, str):
            try:
                keyboard.parse_hotkey(hotkey)
                return True
            except ValueError:
                pass
        return False

    def assign(self):
        HOTKEYS[self.sequence.name] = keyboard.add_hotkey(self.hotkey, self.sequence.execute, args=[self.windows])
 
    def remove(self):
        keyboard.remove_hotkey(HOTKEYS[self.sequence.name])
    
    def __repr__(self):
        windows_repr = ', '.join([f'"{window}"' for window in self.windows])
        return f'Shortcut("{self.hotkey}", {repr(self.sequence)}, [{windows_repr}])'
    
    def __str__(self):
        windows_repr = ' ~ '.join([f'"{window}"' for window in self.windows])
        return f'"{self.hotkey}" : {windows_repr} : {str(self.sequence)}'



# Validate and create shortcut
def validate_shortcut(line):
    # Check if command/line is correctly formatted
    pattern = re.compile(LINE_PATTERN)
    if not pattern.search(line):
        raise SyntaxError(f"Error: Shortcut incorrectly formatted")

    # Split line into sections
    sections = line.split(':')

    hotkey = sections[0].strip()  # get shortcut hotkey
    windows = [window.strip() for window in sections[1].strip().split('~')]  # get list of windows
    sequence_name = sections[2].strip()  # get sequence name
    actions = [
        [item.strip() for item in action.split(';')]
        for action in [part.strip() for part in sections[3].strip().split('~')]
    ]  # get list of sequence actions

    # Convert line information into Sequence object and then Shortcut object
    sequence = convert_sequence([sequence_name, actions])
    shortcut = convert_shortcut([hotkey, sequence, windows])

    # Check if shortcut interferes with an existing shortcut
    if not check_interference(shortcut):
        raise ValueError(f"Error: Shortcut {shortcut.hotkey} interference with existing shortcut")

    return shortcut

# Convert sequence information into a Sequence object
def convert_sequence(sequence):
    # Extract values from sequence information
    sequence_name = sequence[0]
    actions = sequence[1]

    # Loop through actions
    for i in range(len(actions)):
        # Extract values from action information
        type = actions[i][0]
        value = actions[i][1]
        hold = actions[i][2]

        # Validate type and value
        match type:
            case "left_click" | "right_click":
                coord_pattern = re.compile(r"^\((\d+),\s*(\d+)\)$")
                match = coord_pattern.search(value)
                if match:
                    x, y = map(int, match.groups())
                    value = (x, y)
            case "key_press" | "type_string":
                if value[0] in ['"', "'"] and value[0] == value[-1] and len(value) >= 2:
                    value = value[1:-1]
                else:
                    raise SyntaxError(f"Error: String {value} must be enclosed in quotation marks")
            case "wait_time":
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass

        # Validate hold
        if type in ["left_click", "right_click", "key_press", "type_string"]:
            try:
                hold = int(hold)
            except ValueError:
                try:
                    hold = float(hold)
                except ValueError:
                    pass
        if type == "wait_time" and hold == "None":
            hold = None

        # Convert action string to Action object
        actions[i] = Action(type, value, hold)

    # Create and return Sequence object
    return Sequence(sequence_name, actions)

# Convert shortcut information into a Shortcut object
def convert_shortcut(shortcut):
    # Extract values from shortcut information
    hotkey = shortcut[0]
    sequence = shortcut[1]
    windows = shortcut[2]

    # Ensure hotkey is surrounded by ""/''
    if hotkey[0] in ['"', "'"] and hotkey[0] == hotkey[-1] and len(hotkey) >= 2:
        hotkey = hotkey[1:-1]
    else:
        raise SyntaxError(f"Error: Shortcut {hotkey} must be enclosed in quotation marks")

    # Ensure window names are surrounded by ""/''
    for i in range(len(windows)):
        if windows[i][0] in ['"', "'"] and windows[i][0] == windows[i][-1] and len(windows[i]) >= 2:
            windows[i] = windows[i][1:-1]
        else:
            raise SyntaxError(f"Error: Window name {windows[i]} must be enclosed in quotation marks")

    # Create and return Shortcut object
    return Shortcut(hotkey, sequence, windows)

# Check if shortcut interferes with an existing shortcut
def check_interference(shortcut):
    # Loop through existing shortcuts
    for existing in SHORTCUTS.values():
        # Check if a matching hotkey is found
        if shortcut.hotkey == existing.hotkey:
            if "" in shortcut.windows or "" in existing.windows:  # global shortcut, always interferes
                return False
            else:
                for window in shortcut.windows:
                    if any(window in existing_window for existing_window in existing.windows):  # same windows, will interfere
                        return False
    return True
