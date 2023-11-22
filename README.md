# ShortcutMaker

it basically does some given sequence of actions upon pressing a set hotkey

uses commands in a terminal for making and removing shortcuts

GUI coming out some point in the next 20 years probably

now for some grammatically correct english

<br><br>

The application will start minimized to the system tray. To run commands, open the terminal from the system tray icon's "Show Terminal" option. I made the terminal myself because for some reason finding and using a library for a custom terminal window didn't occur to me.

<br><br>

There are 5 types of actions you can put together in a sequence:
- `left_click`: Press down the left mouse button, wait a given amount of time (0 for no hold) and then release the button.
- `right_click`: Press down the right mouse button, wait a given amount of time (0 for no hold) and then release the button.
- `key_press`: Press down a specified key, wait a given amount of time (0 for no hold) and then release the key.
- `type_string`: Type out a series of characters, with a given interval between each character typed.
- `wait_time`: Wait a certain number of seconds (must be greater than 0) before continuing to the next action

<br><br>

To create a shortcut, use the `mk-shortcut` command in the terminal:
```
mk-shortcut shortcut : window ~ ... ~ window : sequence_name : type;value;hold ~ ... ~ type;value;hold
```
- `shortcut`: The shortcut hotkey, surround with `""`.
- `window`: Windows where the shortcut is enabled, use `""` for all windows.
- `sequence_name`: Unique name for the sequence, will be used to identify when using `rm-shortcut`
- `type;value;hold`: Defines an action in the sequence:
  - `type`: Action type (`left_click`, `right_click`, `key_press`, `type_string`, `wait_time`).
  - `value`: Action value (coordinates for clicks, key for key press, string for typing, seconds for waiting).
  - `hold`: Duration to hold the action (button/key down time for clicks/presses, interval between characters for `type_string`, None for `wait_time`).
Note that you cannot use `~`, `:`, or `;` except as separators as mentioned above. Additionally, leading and trailing whitespace at the start or end of items and right before or after colons, semicolons, and tildes are ignored. So something like `type     ;value;      hold` is the same as `type;value;hold`.

<br><br>

To remove a shortcut, use the `rm-shortcut` command in the terminal:
```
rm-shortcut sequence_name
```
- `sequence_name`: Unique name for the sequence

<br><br>

You can also list all the currently active shortcuts and their details by using the `list` command in the terminal:
```
list
```
This will just list all the currently active shortcuts in the same format 

<br><br>

Using the X button on the window will not terminate the program, it will continue run in the background and the terminal will be available through the system tray icon.

To force the program to stop for whatever reason, use `exit` command in the terminal:
```
exit
```
Alternatively, use the "Quit" option in the tray icon's menu.

Both of these will completely stop the program and no more shortcuts will be waited for any more. To restart the program, you can either restart your device or run the `ShortcutMaker.exe` file in the application folder.

<br> <br>

Lastly, maybe something goes wrong with the terminal; usually something about the caret somehow moving somewhere it shouldn't be. If something like that happens, you can press "X" on the terminal, and then use the "Reset Terminal" option from the system tray to relaunch it with everything in the right place.
