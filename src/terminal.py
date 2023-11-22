import tkinter as tk
import pystray
import PIL.Image
import keyboard
from commands import COMMANDS



RESET_FLAG = False
FONT_SIZE = 14  # default font size
MOTD = """========================================
ShortcutMaker v0.1.0
Created by Ali Irfan
Licensed under the MIT License
========================================

> """  # welcome message



# Input a command as a string when enter is pressed
def on_enter(event):
    # Get line from terminal and remove unnecessary characters
    line = text.get("1.0", "end-1c").strip()
    line = line.split("\n")[-1][2:]

    # Attempt to split the line into command and arguments
    count = len(line.split())
    if count == 0:
        command = None
        arguments = None
    elif count == 1:
        command = line
        arguments = None
    else:
        command, arguments = line.split(None, 1)

    # Attempt to run the command
    try:
        result = COMMANDS[command].run(arguments)
        text.insert("end", f"\n{result}\n> ")
    except KeyError:
        text.insert("end", f"\nError: Command {command} is not a valid command\n> ")
    except Exception as e:
        text.insert("end", f"\n{e}\n> ")
    
    # Move caret to end of text
    text.mark_set(tk.INSERT, tk.END)

    return "break"

# Prevent the backspace key from being used past the "> "
def on_backspace(event):
    line = text.get("1.0", "end-1c").split("\n")[-1]
    if line == "> ":
        return "break"

# Prevent arrow keys from being used past the "> "
def on_arrow(event):
    line = text.get("1.0", tk.END)
    current = len(text.get("1.0", tk.INSERT))
    limit = line.rfind("> ") + 2
    if current <= limit or event.keycode in [38, 40]:
        return "break"

# Prevent the mouse from being used within the terminal
def on_click(event):
    return "break"

# Allow zooming in an out with the scroll wheel
def on_scroll(event):
    global FONT_SIZE
    if keyboard.is_pressed("ctrl"):
        if event.delta > 0:
            FONT_SIZE += 1
        else:
            FONT_SIZE -= 1
        text.configure(font=("Courier", FONT_SIZE))

# Prevent shortcuts from being used
def on_shortcut(event):
    return "break"



# Set up the terminal window's widgets
def setup_terminal():   
    # Create the terminal window
    global root
    root = tk.Tk()
    root.configure(bg="black")
    root.title("ShortcutMaker")
    root.iconbitmap("shortcutmakericon.ico")

    # Create the text box
    global text
    text = tk.Text(root, bg="black", fg="white", borderwidth=0, font=("Courier", FONT_SIZE), insertbackground='white', insertwidth=2)
    text.pack(expand=True, fill="both", padx=10, pady=10)

    # Control terminal interaction
    text.bind("<Return>", on_enter)  # input a line of text
    text.bind("<MouseWheel>", on_scroll)  # zoom in and out
    text.bind("<BackSpace>", on_backspace)  # prevent backspace past "> "
    [text.bind(f"<Control-{key}>", on_shortcut) for key in ["a", "t", "i", "h", "slash"]]  # prevent shortcuts

    # Control caret movement
    [text.bind(button.format(num=num), on_click) for button in ["<Button-{num}>", "<B{num}-Motion>", "<ButtonRelease-{num}>"] for num in range(1, 4)]
    [text.bind(key, on_arrow) for key in ["<Left>", "<Up>", "<Down>"]] # prevent/limit caret movement with arrow keys

    # Control window behaviour for system tray icon
    root.protocol("WM_DELETE_WINDOW", hide_terminal)

    # Insert the welcome message
    text.insert("1.0", MOTD)

    # Set the focus on the text box
    text.focus_set()

# Start the terminal
def start_terminal():
    global root
    root.mainloop()



# Hide terminal and show system tray icon
def hide_terminal():
    global root
    root.withdraw()

    # Define system tray icon
    global ICON
    ICON = pystray.Icon(
        "ShortcutMaker",
        PIL.Image.open("shortcutmakericon.ico"),
        menu=pystray.Menu(
            pystray.MenuItem("Show Terminal", show_terminal),
            pystray.MenuItem("Restart Terminal", restart_terminal),
            pystray.MenuItem("Quit", quit)
        )
    )

    ICON.run()

# Show terminal and hide system tray icon
def show_terminal(icon, item):
    global root
    ICON.stop()
    root.deiconify()
    text.focus_set()

# Restart the terminal
def restart_terminal(icon, item):
    global root
    ICON.stop()
    root.destroy()
    setup_terminal()
    root.after(100, start_terminal)

# Exit the program entirely
def quit(icon, item):
    global root
    ICON.stop()
    root.destroy()
