# Screen Readers and the Keyboard

*PadForge read aloud by a screen reader and driven from the keyboard: what you hear, the keys, and the one thing NVDA needs.*

PadForge is tested with NVDA. Every control the Tab key reaches has a name a screen reader speaks, in the language the interface uses. The app looks the same with or without a screen reader.

---

## NVDA and administrator rights

PadForge runs as administrator, and Windows lets a screen reader read an administrator program only when the screen reader can work with one. An installed copy of NVDA can. A portable or temporary copy of NVDA cannot, unless that copy also runs as administrator. Use the installed copy.

## What you hear

- A button that shows only a symbol speaks what its tooltip says, such as "Record" on the record buttons.
- A field or slider speaks the setting it changes: "Web Controller Port, edit, 8080".
- The controller type buttons on the Dashboard and in the sidebar speak as radio buttons, checked on the slot's current type: "Nintendo, radio button, checked".
- The engine and slot power buttons speak as toggle buttons, pressed while on, then their state: "Enabled, toggle button, pressed, Awaiting devices".
- Page titles and section titles are headings.
- Each dialog speaks as a dialog when it opens.
- Status changes are spoken as they happen: the message in the status bar at the bottom of the window, and the status lines on the Dashboard, Settings and Devices pages, such as a server starting or a driver's install status. They are spoken only while PadForge is the active window, so nothing interrupts a game.

## Keys

| Key | What it does |
| --- | --- |
| Tab, Shift+Tab | Move to the next or previous control |
| Space, Enter | Press the focused button |
| Escape | Close the dialog |
| Ctrl+Tab, Ctrl+Shift+Tab | With the focus inside a tab of a controller's page, move to the next or previous tab |
| Alt+Up, Alt+Down | On the Macros tab, move the selected step of the action sequence up or down one place |

---

*Last updated for PadForge 5.0.0.*
