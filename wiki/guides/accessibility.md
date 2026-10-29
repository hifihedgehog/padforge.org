# Screen Readers and the Keyboard

*PadForge read aloud by a screen reader and driven from the keyboard: what you hear, the keys, and the one thing NVDA needs.*

PadForge is tested with NVDA. Every control the Tab key reaches has a name a screen reader speaks, in the language the interface uses. The app looks the same with or without a screen reader, and the keys work without one.

<figure class="pf-video">
<video controls playsinline preload="none" width="1920" height="1080"
       poster="/assets/video/padforge-tutorial-keyboard-and-nvda-poster.jpg"
       aria-label="Video: a controller set up from the keyboard with NVDA, recorded live in PadForge 5.2.2">
<source src="/assets/video/padforge-tutorial-keyboard-and-nvda.mp4" type="video/mp4">
<track kind="captions" srclang="en" label="English" src="/assets/video/padforge-tutorial-keyboard-and-nvda.vtt" default>
</video>
<figcaption>A controller added, a DualSense assigned and the Mappings table opened with the keyboard alone while NVDA reads each control, then a row opened and closed, recorded live in PadForge 5.2.2 in 2 minutes 44 seconds. Long runs of Tab presses are shortened. The narration is a generated voice and the other voice is NVDA, with English captions of both. <a href="/assets/video/padforge-tutorial-keyboard-and-nvda-transcript.txt">Read the transcript</a>.</figcaption>
</figure>

---

## NVDA and administrator rights

PadForge runs as administrator, and Windows lets a screen reader read an administrator program only when the screen reader can work with one. An installed copy of NVDA can. A portable or temporary copy of NVDA cannot, unless that copy also runs as administrator. Use the installed copy.

## What you hear

- A button that shows only a symbol speaks what its tooltip says, such as "Record" on the record buttons.
- A field or slider speaks the setting it changes: "Web Controller Port, edit, 8080".
- The controller type buttons on the Dashboard and in the sidebar speak as radio buttons, checked on the slot's current type: "Nintendo, radio button, checked". The filter chips on the Devices page and the tag chips in the Workshop speak the same way, checked on the current filter.
- The engine and slot power buttons speak as toggle buttons, pressed while on, then their state: "Enabled, toggle button, pressed, Awaiting devices".
- The arrows of a scroll bar or a number box, and the buttons at the top right of the window, speak their names: "Scroll Up", "Increase", "Minimize".
- Each cell of the Mappings table speaks what it holds: the output, the source, the live value, or "Does not apply" for a dead zone the row has no use for.
- A sensitivity curve speaks the point its keys move: "Point 2 of 4, input 50%, output 38%".
- Page titles and section titles are headings.
- Each dialog speaks as a dialog when it opens.
- Status changes are spoken as they happen: the message in the status bar at the bottom of the window, and the status lines on the Dashboard, Settings and Devices pages, such as a server starting or a driver's install status. They are spoken only while PadForge is the active window, so nothing interrupts a game.

## Keys

| Key | What it does |
| --- | --- |
| Tab, Shift+Tab | Move to the next or previous control |
| Space, Enter | Press the focused button, chip, swatch or tile. On a sidebar entry, open its page |
| Escape | Close the dialog or the open list |
| Ctrl+Tab, Ctrl+Shift+Tab | With the focus inside a tab of a controller's page, move to the next or previous tab |
| Alt+Up, Alt+Down | On the Macros tab, move the selected step of the action sequence up or down one place |

A dialog opened from the keyboard starts with the focus on its first control. The Add Controller list and the profile list do the same: the arrow keys and Tab move through them, and Escape closes them and puts the focus back on what opened them.

## The Mappings table

Tab reaches each row of the table, and a row speaks its output and its source.

| Key | What it does |
| --- | --- |
| Tab, Shift+Tab | Move to the next or previous row |
| Enter, Space | Open the row's settings, or close them |

On a row, the arrow keys, Page Up, Page Down, Home, End, letters and digits do nothing. A keyboard can feed the controller you are setting up, and those are the keys it maps, so pressing one to test a mapping never changes the table. The tab's closed pickers ignore the same keys.

## Sensitivity curves

Tab reaches each curve. The point the keys move is drawn orange while the curve has the focus.

| Key | What it does |
| --- | --- |
| Left, Right | Select the point before or after |
| Home, End | Select the first or last point |
| Up, Down | Raise or lower the point's output by 1% |
| Page Up, Page Down | Raise or lower the point's output by 10% |
| Shift+Left, Shift+Right | Move the point's input by 1%, short of the points beside it. The two end points keep theirs |
| Insert | Add a point on the curve, halfway to the next point |
| Delete | Remove the point. The two end points stay |

---

*Last updated for PadForge 5.2.2.*
