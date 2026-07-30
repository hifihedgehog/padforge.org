# NFC Tags

*Tap an NFC tag on a contactless reader to fire a macro. Amiibo-style figures, tag stickers, and cards all work.*

![Register / Manage NFC Tags dialog](../images/nfc-register.png)

PadForge reads NFC tags through a contactless smart-card reader (PC/SC class, such as an ACR122U). Tapping a tag can run a [macro](../guides/macros.md). Register a tag once, give it a name, and bind it like any other button.

---

## The reader as a device

Plug in a PC/SC reader and it shows up on the [Devices](devices.md) page as a device typed **NFC Reader**. Select its card to manage tags and to watch taps live.

The reader exposes buttons you can map:

- **Any NFC Tag**. Fires whenever any tag touches the reader, registered or not.
- One button per tag you have named. Only that tag fires it.

A single tap fires the button once.

---

## Registering a tag

1. On the [Devices](devices.md) page, select the NFC reader.
2. Click **Register / Manage NFC Tags**.
3. In the dialog, tap a tag on the reader. Its UID is captured.
4. Type a name for the tag.
5. Click **Register**.

The dialog lists your registered tags. Each row shows its name and UID with a **Remove** button. Tap another tag to add more.

Tags are keyed by UID, not by reader, so they carry over when you swap readers. They persist across restarts.

---

## Live tag preview

With the NFC reader selected, the Devices page lists your named tags, plus an **Any NFC Tag** row. Tap a tag and its row highlights, so you can confirm the reader sees it and check which tag you just touched.

<!-- SCREENSHOT: nfc-live-preview -->
![NFC reader named-tag list with a tapped tag row highlighted](../images/nfc-live-preview.png)

---

## Using a tag in a macro

1. Add the NFC reader as an input device on the same [slot](controller-slots.md) as the macro.
2. In the macro trigger, pick the NFC reader as the input device.
3. Pick **Any NFC Tag** or a specific named tag.

Tapping that tag runs the macro. See [Macros](../guides/macros.md) for building the action sequence.

---

## Related pages

- [Devices](devices.md): register tags and watch the live preview.
- [Macros](../guides/macros.md): bind a tag tap to an action sequence.

---

*Last updated for PadForge 4.0.0*
