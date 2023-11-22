import shortcuts
import os

# Define a command as a class
class Command:
    def __init__(self, text, action):
        if not isinstance(text, str):
            raise ValueError("Error: Command keyword not of type str")
        self.text = text
        
        if not callable(action):
            raise ValueError("Error: Action function not callable")
        self.action = action

    def run(self, arguments):
        return self.action(arguments)



# Make a shortcut from the terminal
def mk_shortcut(arguments):
    # Validate command
    if not isinstance(arguments, str) or len(arguments) < 1:
        raise SyntaxError(f"Error: Command mk-shortcut requires at least one argument")
    
    # Validate shortcut
    shortcut = shortcuts.validate_shortcut(arguments)
    
    # Add hotkey for shortcut
    try:
        shortcuts.SHORTCUTS[shortcut.sequence.name] = shortcut
        shortcuts.SHORTCUTS[shortcut.sequence.name].assign()
    except KeyError:
        raise ValueError(f"Error: Sequence name {shortcut.sequence.name} already used")
    
    # Save shortcut to file
    with open(shortcuts.SHORTCUTS_FILE, 'r+') as file:
        lines = file.readlines()
        if lines and not lines[-1].strip():
            lines[-1] = f"{arguments}\n"
        else:
            lines.append(f"{arguments}\n")
        file.seek(0)
        file.writelines(lines)
    
    return f"Successfully added {shortcut.sequence.name} ({shortcut.hotkey}) to shortcuts"

# Remove a shortcut from the terminal
def rm_shortcut(arguments):
    # Validate command
    if not isinstance(arguments, str) or len(arguments) < 1:
        raise SyntaxError(f"Error: Command mk-shortcut requires at least one argument")
    
    # Check if shortcut exists
    if arguments in shortcuts.SHORTCUTS:
        # Get hotkey to return with success
        hotkey = shortcuts.SHORTCUTS[arguments].hotkey
        
        # Remove hotkey for shortcut
        shortcuts.SHORTCUTS[arguments].remove()
        del shortcuts.SHORTCUTS[arguments]
        
        # Remove shortcut from file
        with open(shortcuts.SHORTCUTS_FILE, 'r') as file:
            lines = file.readlines()    
        with open(shortcuts.SHORTCUTS_FILE, 'w') as file:
            for i, line in enumerate(lines):
                if arguments != line.strip().split(':')[2].strip():
                    file.write(f"{line.strip()}\n")

        
        return f"Successfully removed {arguments} ({hotkey}) from shortcuts"
    else:
        raise ValueError(f"Error: No existing shortcut with sequence name {arguments} found")

# List curently assigned shortcuts
def list_shortcuts(arguments):
    if arguments:
        raise SyntaxError(f"Error: Command list does not accept arguments")
    
    output = ""
    for shortcut in shortcuts.SHORTCUTS.values():
        output += f"{shortcut}\n"
    return output[:-1]

# Exit the program entirely - very cringe of me to use os._exit() i know
def exit_program(arguments):
    if arguments:
        raise SyntaxError(f"Error: Command exit does not accept arguments")
    os._exit(0)


# Dictionary of valid commands with functions
COMMANDS = {
    "mk-shortcut" : Command("mk-shortcut", mk_shortcut),
    "rm-shortcut" : Command("rm-shortcut", rm_shortcut),
    "list" : Command("list", list_shortcuts),
    "exit" : Command("exit", exit_program)
}
