# Twitch Chat Internals

*How PadForge reads a Twitch channel's chat without signing in, parses viewers' commands, plays them as button presses on the Twitch Chat row, takes turns between viewers, and draws the controller for an OBS browser source.*

For the user-facing side see [Twitch Chat](../features/twitch-chat.md).

| File | Responsibility |
| --- | --- |
| `PadForge.App/Common/Input/Twitch/TwitchChatClient.cs` | `IrcLine`, the socket seam (`IChatSocket`, `WebChatSocket`) and `TwitchChatClient`: the anonymous IRC read, reconnects, duplicate drops, channel names. |
| `PadForge.App/Common/Input/Twitch/ChatCommandParser.cs` | The command language: text to `ChatStep`s, then to a timed list of `ChatEvent`s. |
| `PadForge.App/Common/Input/Twitch/ChatCommandPlayer.cs` | The line of waiting commands and the thread that plays one at a time on the row's buttons. |
| `PadForge.App/Common/Input/Twitch/ChatCommandRegistry.cs` | The word list: stable buttons, validation, the preset words. |
| `PadForge.App/Common/Input/Twitch/ChatTurns.cs` | `!claim`, `!accept`, `!release`, `!skip`, `!skipall` and the notice the picture page shows. |
| `PadForge.App/Common/Input/Twitch/TwitchChatDevice.cs` | The row: an `ISdlInputDevice` that joins the pieces and reads each message. |
| `PadForge.App/Common/Input/Twitch/TwitchChatRuntime.cs` | The Dashboard mirror the engine reads: switch, channel, pause, approval, the open row. `TwitchChatSnapshot` lives here. |
| `PadForge.App/Common/Input/Twitch/ChatGamepadPlacement.cs` | Where the preset words sit in SDL's gamepad layout, for the default mapping. |
| `PadForge.App/Common/Input/InputManager.TwitchChat.cs` | Step 1 phase 1i3: open, retire, recreate and reopen the row. |
| `PadForge.App/Services/InputService.TwitchChat.cs` | The Dashboard status line and flame, the Devices panel line, the picture page's frame, slot lookups and the word list's change handler. |
| `PadForge.App/Services/WebControllerServer.cs` | `DisplayUrl`, the picture page's socket (`HandleDisplayAsync`) and `ChatMessage`. |
| `PadForge.App/WebAssets/display.html`, `js/display_client.js`, `js/layout_view.js` | The picture page. |
| `PadForge.App/Views/ChatCommandsDialog.xaml(.cs)` | The Chat Commands window. |

The chat rules come from references credited on the About page: tmi.js and ComfyJS (reading chat without signing in, the `!` command rule), DougDoug's TwitchPlays template (the newest-20 line), and Yuriy's ForgePlay (the command language and the turn rules, ported to C#). Each rule below names its source where the code does.

---

## The shape

The Twitch Chat row is the Game Telemetry row's shape. One synthetic `ISdlInputDevice` exists while the Dashboard switch is on. The poll thread opens and retires it, and a pooled state copy goes out on every read. The chat connection runs on its own task, so opening the row does no blocking I/O.

```
Dashboard switch + channel -> TwitchChatRuntime -> InputManager.UpdateTwitchChatDevice
    -> TwitchChatDevice ->  TwitchChatClient (anonymous IRC over a WebSocket)
                            -> HandleMessage -> ChatTurns | ChatCommandParser -> ChatCommandPlayer
                            -> GetCurrentState: the player's buttons
    -> WebControllerServer.HandleDisplayAsync -> display.html (OBS)
```

## TwitchChatClient

The client connects to `wss://irc-ws.chat.twitch.tv:443` and logs in anonymously as tmi.js does: the password `SCHMOOPIIE` and a nick of `justinfan` followed by five random digits. DougDoug's template logs in the same way. The login lines are `CAP REQ :twitch.tv/tags twitch.tv/commands`, `PASS`, `NICK`, then `JOIN #channel`. The client sends nothing else but `PONG` and its own `PING`, so it can never post.

`IrcLine.Parse` reads `@tags :prefix COMMAND params :trailing`, with IRCv3 tag escapes undone (an escaped colon is a semicolon, `\s` a space, `\\` a backslash, `\r` and `\n` their characters). `Nick` is the prefix before `!`.

The connection rules:

| Rule | Value | Where it comes from |
| --- | --- | --- |
| Answer each `PING` with a `PONG` carrying its text | | tmi.js |
| Send a `PING` of its own each minute, chat moving or not | `KeepAliveMs` 60,000 | tmi.js `pingLoop` |
| Treat a link with no frame for 90 seconds as dead | `SilenceMs` 90,000 | |
| Count a connect that never finishes as failed | `ConnectMs` 15,000 | |
| Retry delay starts at 1 second and doubles | `FirstRetryMs` 1,000, `MaxRetryMs` 30,000 | tmi.js reconnect timer |
| Reset the delay after a session that joined, or after `RECONNECT` | | tmi.js |
| Reconnect at once on a `RECONNECT` line | | |
| Ask for the join again if nothing answers within 10 seconds, then each minute | `JoinAnswerMs` 10,000 | |
| Drop a message whose `id` tag was among the last 256 | `RememberedIds` 256 | |

The wait for the next `PING` races the pending receive and never cancels it, because canceling a receive ends a `ClientWebSocket`.

Twitch drops a `JOIN` for a channel that does not exist without a word, and answers one for a suspended channel with a `NOTICE`. Neither is a failed connection. The session stays up and `State` reads `NoChat`. The `NOTICE` ids that mean a channel cannot be read are `msg_channel_suspended`, `msg_room_not_found` and `tos_ban`, the ids tmi.js lists under permission errors that concern reading. A `PART` of this session's own nick ends the join the same way.

`TwitchChatState` is `Connecting`, `Reading`, `Retrying` or `NoChat`. `StatusVersion` bumps on each change so the UI rebuilds its line only then.

`PRIVMSG` raises `Message(login, displayName, moderator, broadcaster, text)`. The login is the sender's nick and identifies them, since the display name can be a translation. `broadcaster` is the login equal to the channel, ComfyJS's test. `moderator` is the `mod` tag, or the broadcaster, since ForgePlay counts the broadcaster as a moderator.

`NormalizeChannel` accepts a name or a twitch.tv address (`https://`, `http://`, `www.`, `m.`, `twitch.tv/`, a leading `#`), lowercases it, and returns empty unless it is 1 to 25 letters, digits and underscores.

A host the test gate refuses (`OutboundNetworkGate.RefusesHost`) throws before any socket exists, so the test host never reaches Twitch.

## TwitchChatDevice

The row's identity is fixed so mappings survive a change of channel: the instance GUID is the MD5 of `pftwitch:chat`, the device path is `twitch://chat`, and the type number is `InputDeviceType.TwitchChat` (45). Its vendor and product ids are `0x5457` and `0x4348`. It has no axes, hats, rumble or motion.

Button 0 is **Any Command** (`AnyCommandName`, the English name, translated for display by `MappingDisplayResolver`). Button `n` is the word `ChatCommandRegistry` gave button `n`, named `!word`. `NumButtons` spans `1 + MaxButtonInUse`, so a removed word leaves a gap and nothing renumbers, the voice phrase row's rule.

`HandleMessage` is the one entry for a message, in ForgePlay's order:

1. Trim spaces, combining marks and format characters from the end (`TrimInvisibleEnd`), and anything in U+E0000 to U+E0FFF. Some chat clients append U+034F to repeat a message, and no word holds such a mark.
2. If the text starts with `@name `, drop that reply prefix, as ComfyJS reads a command after one.
3. Ignore anything that does not start with `!`, is longer than 500 characters, or arrives while paused.
4. Split the body at its first space. The first word, lowercased, is the command and the next word is its argument.
5. Offer it to `ChatTurns.Handle`. If it was a turn command and someone now holds control, `KeepOnly` removes waiting commands the owner may not play.
6. Otherwise ignore it if `ChatTurns.CanPlay` says no.
7. Parse the command word and the rest as one sequence. A null result is ignored. Otherwise enqueue a `ChatPlay` with the user, login, moderator flag, text, events and end time.

`Snapshot()` copies everything the picture page shows into a `TwitchChatSnapshot`. `ShowVersion` is the sum of the player, turns, status, pause and approval versions, so the page is sent chat only when something moved.

## ChatCommandRegistry

The registry is the voice phrase registry's shape: a static list, a stable button per word, a `RegistryChanged` event raised outside its lock, a `ButtonFreed` event with the freed button raised before it, and a `LoadRegistry`/`SaveRegistry` pair that `SettingsService` round-trips through the `ChatCommands` array of `PadForge.xml`.

| Constant | Value |
| --- | --- |
| `MaxWords` | 128 |
| `MaxWordLength` | 20 |
| `UsualWords` | a, b, x, y, lb, rb, lt, rt, select, start, ls, rs, up, down, left, right |
| `ReservedWords` | claim, accept, release, skip, skipall |

`Check` returns a `WordProblem`: `Empty`, `TooLong`, `Characters` (not a letter first, or a character that is not a letter or digit), `EndsInTime` (the parser's time pattern matches the end) or `Reserved`. `Add` takes the lowest free button and never changes it. `LoadRegistry(null)` registers the usual words at buttons 1 to 16, and the list starts with them before any load, so a first run with no `PadForge.xml` saves them too. An empty saved list stays empty, because the streamer removed them. A saved entry with a bad, out-of-range or taken button gets the lowest free one.

`Remove` raises `ButtonFreed`, which `InputService.OnChatWordFreed` turns into `FreedButtonCleanup.ForChatWord` on the UI thread. That clears every mapping that reads the button on the row: pad settings, saved profiles, the default profile's pending snapshot, global and per-pad macros, and the output-surface mappings. `RegistryChanged` makes `InputService.OnChatCommandRegistryChanged` re-derive the row's objects (`RefreshChatObjects`), refresh the Devices preview and the mapping pickers, and save.

## ChatGamepadPlacement

`ChatGamepadPlacement.For()` gives `SettingsManager.CreateDefaultPadSetting` the positions of the words the list holds now: a, b, x, y, lb, rb, select, start, ls, rs on the ten gamepad buttons, lt and rt on the trigger axes, and up, down, left, right on the D-pad. It is the placement path Bliss-Box ports use. A removed preset word yields no source. Home and the touchpad are never placed.

## ChatCommandParser

`Parse(text, buttonFor)` returns the steps, or null when the row does not play the text. `buttonFor` is `ChatCommandRegistry.ButtonFor`, below 1 for an unknown word. The tokenizer splits on whitespace outside brackets and counts bracket depth.

| Token | Meaning |
| --- | --- |
| `a` | Press, `DefaultPressMs` (200) |
| `a500ms`, `a1.5s` | Press with that hold. The time at the end of a token is read with `(\d+(?:\.\d+)?)(ms\|s)$`. |
| `a+b` | Actions that start together. The step lasts as long as its longest timed action. |
| `_a` | Hold until released or until the command ends |
| `-a` | Release. With a time, press again after it. |
| `#500ms` | A pause |
| `[a b]*3` | Repeat the group, 1 to 50 times |
| `[a+b]500ms` | Give each press in the group that hold |

The limits: `MaxCommandMs` 10,000, `MaxSteps` 50 (repeats included), `MaxNesting` 4, `MaxLength` 500, `MaxGroupParses` `MaxSteps * MaxNesting` (200). A time over 10 seconds is refused when it is read, before it can overflow a sum. An empty group is refused, since it would never reach the step limit however often it repeated. Any rule broken throws a private `Rejected`, and `Parse` returns null, so a command with one bad word plays nothing.

`Timeline` turns steps into `ChatEvent(AtMs, Button, Down)` and the end time. A step's actions start together and the step waits for the longest. Every button still down at the end is released then, ForgePlay's reset. The row's buttons are read as levels, so a press that landed on its own release would read as one long hold. Each press of a button therefore waits until the button has been up for `ReleaseGapMs` (50, two frames at 40 Hz), and that wait counts toward the 10 seconds. Events sort stably by time, so presses and releases that share a moment keep the order the command gave them.

## ChatCommandPlayer

One background thread (`PadForge Twitch commands`) plays one `ChatPlay` at a time. `MaxWaiting` is 20: `Enqueue` appends and removes from the front while the line is over 20, DougDoug's `MAX_QUEUE_LENGTH`. `Enqueue` reads `TwitchChatRuntime.Paused` under the same lock the pause's clearing takes, so no command slips in behind it.

`Run` takes the first waiting play, makes it current, holds button 0, waits to each event's time with `WaitUntil`, and sets the button level. A skip bumps `_skips`, which `WaitUntil` compares against the count it started with, so a skip ends the wait at once. At the end, or on a skip, every button clears and the player waits out `ReleaseGapMs` before the next command, so two viewers' presses of one button read as two. The command stays current through the gap, so the picture page shows no idle line between commands.

| Member | Behavior |
| --- | --- |
| `Skip(all)` | Stops the current command, and with `all` clears the line. False when there was nothing to stop. |
| `KeepOnly(mayPlay)` | Drops waiting plays the predicate refuses and skips the current one if refused. Used when a viewer takes control. |
| `ClearWaiting()` | Clears the line, leaves the current command. |
| `CopyButtons(span)` | The row's read: button 0 and the held words. |
| `NextWaiting(max)` | The first commands in line, for the picture page. |

`Dispose` joins the thread for 50 ms, since the row closes on the poll thread, and closes the wake event only once the thread has ended.

## ChatTurns

`ChatTurns` is ForgePlay's `ClaimControl` and `SkipControl`. It keeps its own lock and a monotonic clock that tests replace.

| Constant | Value |
| --- | --- |
| `ControlMs` | 300,000 |
| `VoteMs` | 60,000 |
| `RequiredVotes` | 2 |
| `MaxPendingRequests` | 5 |
| `SkipWindowMs` | 30,000 |
| `SkipConfirmations` | 2 |

`TwitchClaimApproval` is saved by number: `Streamer` 0, `Moderators` 1, `Viewers` 2. `Approves` is true for the broadcaster, and for a moderator unless the choice is `Streamer`. It is read on every command, so a change applies with no reopening, and `VotesNeeded` is 2 only under `Viewers`. An approver's `!accept @name` or `!claim @name` grants at once. Under `Viewers`, two other viewers' do too, counted by login. A viewer cannot approve their own request.

A viewer is known by login and shown by the name Twitch gives. `@name` finds a request by either. A grant to a name typed with no request behind it matches that name as either, since only the viewer's next message says which it was.

`Skip` needs a command playing. A moderator's skip acts at once. Others open a vote, and a second distinct login within `SkipWindowMs` confirms it. The skip itself is the callback `all => _player.Skip(all)`, run outside the turns lock because the player takes its own.

PadForge posts nothing in chat, so every result is a `Notice` string the picture page shows. The text is English and never repeats what a viewer typed: an unknown target from someone who cannot approve is answered without its text.

## TwitchChatRuntime

Static, written by the Dashboard view model on the UI thread and read by the poll thread, the row and the picture page. `Enabled` and `Channel` bump `Version` (the channel only while enabled), and the sweep reopens the row when `Version` moves. `Paused` and `ClaimApproval` act on the open row at once, with their own version counters. `Paused` is not saved and turning the switch off clears it. `Live` is the open row. `Skip()`, `ClearLine()` and `EndClaim()` reach it for the card's buttons.

`SettingsService` stores `EnableTwitchChat`, `TwitchChatChannel` and `TwitchChatClaimApproval` in `AppSettings` alone, and `ChatCommands` beside them. None is in `ProfileData`, so a profile switch never opens or closes the connection. `MainWindow` saves on a change of any of the three.

## InputService.TwitchChat

`BuildTwitchChatStatus(channel, state, paused)` builds the one line the Dashboard card and the Devices row share, from `TwitchChat_Status_*` strings, with the paused suffix. The Dashboard line is cached on the row instance, its `StatusVersion` and the pause, since a reopen restarts the version at 0. `IsTwitchChatOpen` enables the card's buttons and `IsTwitchChatRunning` lights its flame, true while the state is `Reading`.

`DisplayFrameFor(slot)` is the picture page's view of a slot: its combined output (raw HID state for a Nintendo slot or a Valve lettered one, the gamepad otherwise, the pad page's rule), the layout key from the slot's 2D asset folder (`WebLayoutFor`) and the pad's saved finish. It returns null while the slot is off. `FirstTwitchChatSlot` is the lowest `MapTo` among the row's assignments. `ShownSlotNumber` is the number PadForge shows for a slot, which `?slot=` uses.

## The picture page

`WebControllerServer.DisplayUrl` is `<plain base>/display.html?code=<access code>`, or null while the plain address is not served. The Dashboard sets `TwitchChatDisplayUrl` from it. The main address will not do. Its certificate is self-signed, and obs-browser passes no ignore-certificate-errors switch and leaves CEF's `OnCertificateError` at its default, which cancels the page.

The page opens `/ws?view=<slot>&code=<code>`. A socket with `view` goes to `HandleDisplayAsync`, which makes no device and takes no client slot. At most `MaxDisplays` (4) run at once and a fifth gets a 503. Every 33 ms the loop does the following:

- Asks `DisplaySlotFor(view)` once a second: a named number first, else the Twitch row's first slot, else the first slot shown.
- Sends a `slot` message when the slot, layout or finish changed.
- Sends a `state` message when the pose changed.
- Sends a `chat` message when `ShowVersion` moved or a second passed, so a claim's clock counts down. With the feature off the message is `on: false` and the page hides its panel.

A page that joined through the plain address with a code the streamer has since replaced is closed, as `SetPlainAccessCode` closes the plain controllers. The page is transparent, sends nothing, and reconnects after 3 seconds. It clips a command to 60 characters, shows a turn notice for 15 seconds, and lists the first five waiting commands (`TwitchChatDevice.ShownWaiting`). `?layout=` and `?finish=` override the drawing, and WLG is Yuriy's finish.

The web controller's landing page and controller pages send the viewer's name (`?name=`, kept in the browser's local storage, 24 characters at most, cleaned by `CleanViewerName`), so the Devices page names each phone.

## Tests

- `TwitchChatCommandTests`: the registry (preset words at buttons 1 to 16, gaps, the word rules, restore, the settings round trip, change events), the parser (presses, holds, chords, groups, repeats, rejects, the 10 second and 50 step limits, the release gap, the parse budget) and `ChatTurns` on a fake clock (each approval choice, the 60 second request and five-request limits, skips by two viewers or one moderator, login against shown name, notices that never repeat a viewer's text).
- `TwitchChatRowTests`: `IrcLine` parsing and unescaping, `PING` and `RECONNECT`, the scripted socket (joining, duplicate ids, the ping schedule, the silence and connect limits, `NoChat` and its re-ask, the retry delay doubling to 30 seconds), channel names, the player (the newest 20, `Any Command`, skips, the gap), the row's identity and buttons, replies and pause, control and the line, invisible suffixes, default placement, `FreedButtonCleanup` against every place a button can be mapped, the Dashboard switch and approval reaching the runtime, the status line, the picture page's slot choice, `DisplayUrl` and the chat message.
- The test host never reaches Twitch: `InTheTestHostTheClientNeverReachesTwitch` builds a client whose socket factory is never called, and `TestHostFenceTests` pins the gate check in `SessionAsync`.

---

*Last updated for PadForge 5.3.0.*
