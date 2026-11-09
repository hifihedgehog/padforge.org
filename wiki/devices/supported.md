# Supported Devices

*Every controller, wheel, stick, adapter and lit device PadForge knows by name, in one place.*

PadForge recognizes **2,667** devices by their USB identity: 606 gamepads in SDL's controller list, 289 more pads that the community SDL_GameControllerDB maps, 4 Flydigi pads, 68 pads and specialty devices that SDL's dedicated drivers claim, 86 racing wheels, 24 flight sticks, 4 throttles, 32 arcade sticks, 10 GameCube adapters, 24 devices PadForge's own code claims, the PS VR Aim Controller, which PadForge's own mapping file names, and 1,563 RGB keyboards, mice, headsets and other devices PadForge lights itself, [listed below](#rgb-keyboards-mice-and-other-lit-devices). The arcade sticks, three wheels and two adapters also sit in the gamepad list, and seven of the lit devices are controllers counted above, so the total is smaller than the sum. Behind those sit **464** named gamepad mappings: 248 from SDL's Windows database, 214 more from the community database, and PadForge's own two, for the DualShock 3 under DsHidMini and the PS VR Aim Controller. For virtual controllers, HIDMaestro ships 337 device profiles. PadForge's controller pickers offer the 136 controllers that carry a captured HID descriptor, and a Keyboard+Mouse slot can send through any of its 51 keyboards and 52 mice, [listed below](#virtual-keyboards-and-mice).

!!! tip "Not on this list?"
    It very likely still works. Anything Windows enumerates as an input device can be read
    as a mapping source, including generic DirectInput joysticks, keyboards, mice, touchpads
    and MIDI gear. This list is where the **names, the correct button layout and the extra
    capabilities** come from, not the boundary of what PadForge accepts. A pad that is not
    listed appears as a generic controller and maps the same way.

---

## Gamepads

Grouped by the family each pad reports as. A third-party pad in an Xbox 360 or PlayStation 4
family gets that family's layout and works everywhere that family does.

### Xbox 360 (146)

| Vendor | Devices |
| --- | --- |
| **Mad Catz** | Mad Catz Beat Pad, Mad Catz Brawlstick for Xbox 360, Mad Catz Call Of Duty, Mad Catz Fightpad, Mad Catz FightStick SoulCaliber, Mad Catz FightStick TE2, Mad Catz FightStick TES+, Mad Catz FPS Pro, Mad Catz Gamepad2, Mad Catz JOYTECH NEO SE Advanced GamePad, Mad Catz MicroCon Gamepad, Mad Catz MicroCon GamePad Pro, Mad Catz MLG FightStick TE, Mad Catz MvC2 TE, Mad Catz Precision Bass Guitar, Mad Catz SFxT Fightstick Pro, Mad Catz Street Fighter IV FightPad, Mad Catz Street Fighter IV FightStick SE, Mad Catz Street Fighter IV SE Fighting Stick, Mad Catz Wired Xbox 360 Controller, Mad Catz Wired Xbox 360 Controller (SFIV), Mad Catz Wireless Precision Bass Guitar, Mad Catz Wireless Rock Band Guitar, Mad Catz Xbox 360 Controller, Mad Catz Xbox controller - MW2, MadCatz GamePad, Street Fighter IV Arcade Stick TE - Chun Li, Street Fighter IV FightPad, Street Fighter IV FightStick TE |
| **HORI** | Hori Co. DOA4 FightStick, Hori Fighting Commander ONE, Hori Fighting Edge, Hori Fighting Stick EX2, Hori Fighting Stick EX2B, Hori Fighting Stick VX, Hori Fighting Stick VX Alt, Hori Fighting Stick α, Hori GEM Xbox controller, Hori PAD A, Hori PadEX Turbo, Hori Real Arcade Pro 4, Hori Real Arcade Pro V Kai 360, Hori Real Arcade Pro VX, Hori Real Arcade Pro VX-SA, Hori Real Arcade Pro. EX, Hori Real Arcade Pro.EX, Hori Real Arcade Pro.EX Premium VLX, Hori Real Arcade Pro.VX SA, HORI Slime Controller, Hori SOULCALIBUR V Stick, Hori XBOX 360 EX 2 with Turbo |
| **PDP** | Afterglow Gamepad 1, Afterglow Gamepad 3, PDP AFTERGLOW AX.1, PDP Afterglow AX.1, PDP Battlefield 4 Controller, PDP EA Soccer Controller, PDP INJUSTICE FightPad, PDP INJUSTICE FightStick, PDP MK X Fight Stick, PDP Versus Fighting Pad, PDP Xbox 360 Afterglow, PDP Xbox 360 Controller, PDP Xbox 360 Marvel Controller, PDP Xbox 360 Rock Candy, Rock Candy Gamepad for Xbox 360 |
| **Rock Band** | Rock Band 2 Wireless Guitar, Rock Band Keyboard (Mustang), Rock Band MIDI Pro Adapter (Keyboard), Rock Band MIDI Pro Adapter (Mustang Guitar), Rock Band MIDI Pro Adapter (Squire Guitar), Rock Band Pro Guitar (Mustang), Rock Band Pro Guitar (Squire), Rock Band Wireless Bass Guitar |
| **Razer** | Razer Atrox Arcade Stick, Razer Onza, Razer Onza Classic Edition, Razer Onza TE, Razer Onza Tournament Edition, Razer Sabertooth |
| **Guitar Hero** | Guitar Hero 5 Guitar, Guitar Hero Live Guitar, Guitar Hero Wireless Drum Kit, Guitar Hero Wireless Guitar, Guitar Hero World Tour Kiosk |
| **Logitech** | Logitech Chillstream Controller, Logitech Gamepad F310, Logitech Gamepad F510, Logitech Gamepad F710 |
| **Thrustmaster** | Thrustmaster Ferrari 458 Racing Wheel, ThrustMaster Ferrari Italia 458 Racing Wheel, Thrustmaster Gamepad GP XID, Thrustmaster, Inc. GPX Controller |
| **Xbox 360** | Xbox 360 Controller, Xbox 360 Pro EX Controller, Xbox 360 Wireless Controller, Xbox 360 Wireless Racing Wheel |
| **Harmonix** | Harmonix Rock Band 1 Guitar, Harmonix Rock Band Drumkit, Harmonix Xbox 360 Controller |
| **RedOctane** | RedOctane Controller, RedOctane Controller Adapter, RedOctane Guitar Hero X-plorer |
| **DJ** | DJ Hero Turntable, DJ Hero Turntable (Wireless) |
| **Power** | Power Gig Drums, Power Gig Guitar |
| **PowerA** | PowerA MINI PROEX Controller, PowerA Pro Ex |
| **Saitek** | Saitek Cyborg Rumble Pad - PC/Xbox 360, Saitek P3200 Rumble Pad - PC/Xbox 360 |
| **SteelSeries** | SteelSeries Nimbus/Stratus XL, SteelSeries Stratus Duo |
| **Amazon** | Amazon Luna Controller |
| **Aplay** | Aplay Controller |
| **ASUS** | ASUS ROG Ally X built-in controller |
| **Band** | Band Hero Wireless Drum Kit |
| **Batarang** | Batarang Xbox 360 controller |
| **BigBen** | BigBen Interactive XBOX 360 Controller |
| **CRKD** | CRKD Guitar |
| **Elecom** | Elecom JC-U3613M |
| **FUS1ON** | FUS1ON Tournament Controller |
| **GameSir** | Gamesir Xbox Controller |
| **Gamestop** | Gamestop Xbox 360 Controller |
| **GPD** | GPD Win 2 X-Box Controller |
| **Homemade** | Homemade fightstick based on brook pcb |
| **Honey** | Honey Bee Xbox360 dancepad |
| **HoriPad** | HoriPad EX2 Turbo |
| **HSM3** | HSM3 Xbox360 dancepad |
| **ION** | ION Drum Rocker |
| **Joytech** | Joytech Neo-Se Take2 |
| **logitech** | logitech xinput |
| **Mad** | Mad Cats Ghost Recon FS GamePad |
| **Microsoft** | Microsoft Xbox 360 Big Button IR |
| **MLG** | MLG Pro Circuit Controller (Xbox) |
| **Mortal** | Mortal Kombat Klassic FightStick |
| **MortalKombat** | MortalKombat FightStick |
| **NACON** | Nacon GC-100XF |
| **Nvidia** | Nvidia Shield local controller |
| **NVIDIA** | NVIDIA Shield streaming controller |
| **Power A** | Power A Mini Pro Elite |
| **PXN** | PXN V900 |
| **Super** | Super SFIV FightStick TE S |
| **Tron** | Tron Xbox 360 controller |
| **Wooting** | Wooting Two |
| **Xbox** | Xbox Airflo wired controller |

### Xbox One and Series (79)

| Vendor | Devices |
| --- | --- |
| **PDP** | PDP Battlefield 1 Controller, PDP Deliverer of Truth, PDP Fallout 4 Vault Boy Controller, PDP Halo Wars 2 Face-Off Controller, PDP Kingdom Hearts Controller, PDP Mass Effect: Andromeda Controller, PDP Metallic Controller, PDP Mirror's Edge Controller, PDP MK X Fight Pad, PDP Mortal Kombat Controller, PDP NFL Face-Off Controller, PDP One-Handed Joystick Adaptive Controller, PDP Titanfall 2 Controller, PDP Victrix Pro Fight Stick, PDP Xbox One @Play Controller, PDP Xbox One Afterglow, PDP Xbox One Aqualime, PDP Xbox One Arctic White, PDP Xbox One Blu-merang, PDP Xbox One Camo, PDP Xbox One Controller, PDP Xbox One Cranblast, PDP Xbox One Crimson Red, PDP Xbox One Ember Orange, PDP Xbox One Face-Off Controller, PDP Xbox One GAMEware Controller, PDP Xbox One Ghost White, PDP Xbox One Midnight Blue, PDP Xbox One Phantasm Red, PDP Xbox One Phantom Black, PDP Xbox One Raven Black, PDP Xbox One RC Gamepad, PDP Xbox One Red Camo, PDP Xbox One Revenant Blue, PDP Xbox One Rock Candy, PDP Xbox One Royal Purple, PDP Xbox One Specter Violet, PDP Xbox One Verdant Green, PDP Xbox Series X Afterglow, PDP Xbox Series X Midnight Blue, Victrix Gambit Tournament Controller |
| **PowerA** | PowerA FUSION Controller, PowerA Fusion Fight Pad, PowerA Fusion Pro 2 Controller, PowerA FUSION Pro Controller, PowerA MOGA XP-Ultra Controller, PowerA Spectra Infinity Controller, PowerA Xbox One Controller, PowerA Xbox One Mini Wired Controller, PowerA Xbox Series X Controller |
| **HORI** | HORI Fighting Commander, HORI Fighting Commander OCTA for Xbox Series X, Hori Real Arcade Pro Hayabusa (USA) Xbox One, Hori Real Arcade Pro V Kai Xbox One, HORIPAD ONE |
| **Xbox One** | Xbox One Controller, Xbox One Elite 2 Controller, Xbox One Elite Controller, Xbox One S Controller, Xbox ONE spectra |
| **Razer** | Razer Atrox Arcade Stick, Razer Wildcat, Razer Wolverine Tournament Edition, Razer Wolverine Ultimate |
| **8BitDo** | 8BitDo Ultimate 2C Wireless Controller, 8BitDo Ultimate Wired Controller, 8BitDo Ultimate Wired Controller for Xbox |
| **BDA** | BDA XB1 Classic Controller, BDA XB1 Spectra Pro |
| **Hyperkin** | Hyperkin Duke, Hyperkin X91 |
| **Turtle Beach** | Turtle Beach REACT-R, Turtle Beach Recon Controller |
| **Xbox** | Xbox Adaptive Controller, Xbox Controller Mode for NACON Revolution 3 |
| **HP** | HP HyperX Clutch Gladiate |
| **Mad Catz** | Mad Catz FightStick TE 2 |
| **Thrustmaster** | ThrustMaster eSwap PRO Controller Xbox |
| **Xbox Series** | Xbox Series X Controller |

### PlayStation 3 (68)

| Vendor | Devices |
| --- | --- |
| **PS3** | PS3 / Wii U Guitar Hero Live Guitar, PS3 DJ Hero Turntable, PS3 Guitar Hero Drums, PS3 Guitar Hero Guitar, PS3 Midi Pro Adapter - Drums Mode, PS3 Midi Pro Adapter - Keyboard Mode, PS3 Midi Pro Adapter - Mustang Guitar Mode, PS3 Midi Pro Adapter - Squire Guitar Mode, PS3 Mustang Guitar, PS3 Rock Band Drums, PS3 Rock Band Guitar, PS3 Rock Band Keyboard, PS3 Squire Guitar |
| **Wii** | Wii RB1 Drums, Wii RB1 Guitar, Wii RB2 Drums, Wii RB2 Guitar, Wii RB3 Keyboard, Wii RB3 Midi Pro Adapter - Drums Mode, Wii RB3 Midi Pro Adapter - Keyboard Mode, Wii RB3 Midi Pro Adapter - Mustang Guitar Mode, Wii RB3 Midi Pro Adapter - Squire Guitar Mode, Wii RB3 Mustang Guitar, Wii RB3 Squire Guitar |
| **HORI** | HORI BDA GP1, HORI Fighting Commander 4 PS3, HORI Fighting Commander PC, HORI Fighting Commander PS3, HORI Fighting Stick mini 4, HORI horipad4 ps3, Horipad 3, Real Arcade Pro 4 |
| **PDP** | afterglow ps3, Afterglow PS3, PDP Afterglow Wireless PS3 controller, PDP Versus Fighting Pad, Rock Candy PS3, Rock Candy PS4 |
| **Mad Catz** | Mad Catz Alpha PS3 mode, Mad Catz Alpha PS4 mode, Mad Catz FightStick TE 2+ PS3, Madcatz Fightstick Pro |
| **Qanba** | Qanba Dragon, Qanba Drone, Qanba Obsidian, Qanba Q1 fight stick |
| **PS2** | PS2, PS2 ACME GA-D5 |
| **BDA** | BDA Pro Ex |
| **BTP** | BTP 2163 |
| **Cyborg** | Cyborg V3 |
| **Digiflip** | Digiflip GP006 |
| **Firestorm** | Firestorm Dual Analog 3 |
| **gioteck** | gioteck vx2 |
| **Green** | Green Asia |
| **JC-U3412SBK** | JC-U3412SBK |
| **JC-U4113SBK** | JC-U4113SBK |
| **Logitech** | Logitech Chillstream |
| **madcats** | madcats fightpad pro ps3 |
| **Power A** | Power A PS3 |
| **ps2** | ps2 |
| **Retro** | Retro Controller |
| **ShanWan** | ShanWan PS3 |
| **Sony** | Sony PS3 Controller |
| **SpeedLink** | SpeedLink Strike FX |
| **SRXJ-PH2400** | SRXJ-PH2400 |
| **Thrustmaster** | Thrustmaster wireless 3-1 |
| **Venom** | Venom Arcade Stick |

### PlayStation 4 (65)

| Vendor | Devices |
| --- | --- |
| **NACON** | NACON Asymmetric Controller, NACON Asymmetric Controller Wireless Dongle, NACON Daija Arcade Stick, NACON Daija Fight Stick, Nacon PS4 Compact Controller, NACON PS4 controller in Xbox mode, NACON Revolution 5 Pro, NACON Revolution 5 Pro (PS4 mode wired), NACON Revolution Infinite, Nacon Revolution Pro Controller, NACON Revolution Pro Controller 3, Nacon Revolution Pro Controller v2, NACON Revolution Unlimited, NACON Revolution Unlimited Wireless Dongle, NACON Wireless Controller for PS4 |
| **HORI** | HORI Fighting Commander 4 PS4, HORI Fighting Commander OCTA, HORI Fighting Commander PS4, HORI Fighting Stick mini 4, Hori Fighting Stick mini 4 kai, Hori Fighting Stick α, Hori mini wired, HORI Real Arcade Pro 4, HORI TAC PRO mousething, HORI TAC4 mousething, HORI Wireless Controller Light, HORIPAD 4 FPS, HORIPAD 4 FPS Plus |
| **Razer** | Razer Panthera Evo Fightstick, Razer Panthera PS4 Controller, Razer Raiju 2 Tournament edition BT, Razer Raiju 2 Tournament edition USB, Razer Raiju 2 Ultimate BT, Razer Raiju 2 Ultimate USB, Razer Raiju PS4 Controller, Razer RAION Fightpad |
| **Qanba** | Qanba Dragon, Qanba Dragon Arcade Joystick, Qanba Drone, Qanba Obsidian, Qanba Obsidian Arcade Joystick |
| **Mad Catz** | Mad Catz FightPad Pro PS4, Mad Catz FightStick TE 2 PS4, Mad Catz FightStick TE 2+ PS4, Mad Catz FightStick TE S+ PS4 |
| **PDP** | Victrix Pro FS, Victrix Pro FS PS4/PS5 (PS4 mode), Victrix Pro FS V2 w/ Touchpad for PS4 |
| **Armor** | Armor 3 or Level Up Cobra, Armor Armor 3 Pad PS4 |
| **Astro** | Astro C40, Astro C40 in Xbox 360 mode |
| **Sony** | Sony PS4 Controller, Sony PS4 Slim Controller |
| **Brook** | Brook Mars Controller |
| **EMIO** | EMIO PS4 Elite Controller |
| **Game:Pad** | Game:Pad 4 |
| **GameStop** | GameStop PS4 Fun Controller |
| **Hitbox** | Hitbox Arcade Stick |
| **P4** | P4 Wired Gamepad generic knock off |
| **PowerA** | PowerA Fusion Fight Pad |
| **STRIKEPAD** | STRIKEPAD PS4 Grip Add-on |
| **Thrustmaster** | Thrustmaster Eswap Pro |
| **Venom** | Venom Arcade Stick |
| **ZEROPLUS** | ZEROPLUS P4 Wired Gamepad |

### PlayStation 5 (15)

| Vendor | Devices |
| --- | --- |
| **Razer** | Razer Kitsune, Razer Raiju V3 Pro, Razer Raiju V3 Pro (PS5 mode wired), Razer Wolverine V2 Pro, Razer Wolverine V2 Pro (Wireless) |
| **Backbone** | Backbone One PlayStation Edition for iOS, Backbone One PlayStation Edition Gen 2 |
| **HORI** | HORI Fighting Commander OCTA, Hori Fighting Stick α |
| **NACON** | NACON Revolution 5 Pro, NACON Revolution 5 Pro (PS5 mode wired) |
| **Sony** | Sony DualSense Controller, Sony DualSense Edge Controller |
| **Access** | Access Controller for PS5 |
| **PDP** | Victrix Pro FS PS4/PS5 (PS5 mode) |

### Nintendo Switch (33)

| Vendor | Devices |
| --- | --- |
| **PDP** | PDP Afterglow Wave Wired/Wireless Controller for Switch, PDP Afterglow Wired Deluxe+ Audio Controller, PDP Afterglow Wireless Switch Controller, PDP Faceoff Deluxe Wired Pro Controller for Nintendo Switch, PDP Faceoff Wired Deluxe+ Audio Controller, PDP Faceoff Wired Pro Controller for Nintendo Switch, PDP REALMz Wireless Controller, PDP Rockcandy Wired Controller, PDP Wired Fight Pad Pro for Nintendo Switch |
| **Nintendo Switch** | Nintendo Switch 2 Joy-Con, Nintendo Switch 2 Joy-Con (Left), Nintendo Switch 2 Joy-Con (Right), Nintendo Switch Joy-Con, Nintendo Switch Joy-Con (Left), Nintendo Switch Joy-Con (Right), Nintendo Switch Pro Controller |
| **PowerA** | PowerA Nintendo Switch Fusion Fight Pad, PowerA Nintendo Switch Fusion Pro Controller - USB, PowerA Nintendo Switch Nano Wired Controller, PowerA Nintendo Switch Spectra Controller, PowerA Super Mario Controller, PowerA Wired Controller Nintendo GameCube Style, PowerA Wired Controller Plus |
| **HORI** | HORI Pokken Tournament DX Pro Pad, HORI Real Arcade Pro V Hayabusa in Switch Mode, HORI Taiko Controller For Switch, HORI Wireless Switch Pad, HORIPAD for Nintendo Switch, HORIPAD S |
| **ZUIKI** | ZUIKI MasCon for Nintendo Switch, ZUIKI MasCon for Nintendo Switch Black, ZUIKI MasCon for Nintendo Switch Red |
| **Power A** | Power A Fusion Wireless Arcade Stick (USB Mode) |

### Nintendo Switch 2 (6)

| Vendor | Devices |
| --- | --- |
| **Turtle Beach** | Turtle Beach Afterglow Wave Wired Controller for Nintendo Switch 2, Turtle Beach Afterglow Wired Controller for Switch 2, Turtle Beach Afterglow Wireless RGB Gaming Controller for Nintendo Switch 2, Turtle Beach Rematch Wired Controller for Nintendo Switch 2, Turtle Beach Rematch Wireless RGB Gaming Controller for Nintendo Switch 2 |
| **Nintendo Switch** | Nintendo Switch 2 Pro Controller |

### Steam (13)

| Vendor | Devices |
| --- | --- |
| **Valve** | Valve Bluetooth Steam Controller (D0G), Valve Bluetooth Steam Controller (HEADCRAB), Valve Legacy Steam Controller (CHELL), Valve Steam Deck Builtin Controller, Valve Steam Nereid Dongle (Proprietary), Valve Steam Proteus Dongle (Proprietary), Valve Steam Triton Controller, Valve Steam Triton Controller (BLE), Valve wired Steam Controller (D0G), Valve wired Steam Controller (HEADCRAB), Valve wireless Steam Controller |
| **HORI** | HORI Wireless HORIPAD for Steam, HORI Wireless HORIPAD for Steam ( BT ) |

### 8BitDo (5)

| Vendor | Devices |
| --- | --- |
| **8BitDo** | 8Bitdo Pro 2 Controller, 8Bitdo Pro 3 Controller, 8Bitdo SF30 Controller, 8Bitdo SN30 Controller, 8Bitdo Ultimate 2 Wireless Controller |

### Flydigi (4 USB identities)

SDL's Flydigi driver claims these pads by USB identity, then names the model from the controller's own device ID, so one identity covers a family.

| Identity | What the driver claims |
| --- | --- |
| **04B4:2412** | First-generation Flydigi gamepad (vendor protocol on interface 2) |
| **37D7:2501** | Second-generation Flydigi Apex |
| **37D7:2502** | Second-generation Flydigi Apex 6 |
| **37D7:2401** | Second-generation Flydigi Vader |

Models the driver names from the device ID: Apex 2, Apex 3, Apex 4, Apex 5, Apex 6, Vader 2, Vader 2 Pro, Vader 3, Vader 3 Pro, Vader 4 Pro and Vader 5 Pro.

The four rear paddles map as Right Paddle 1 and 2 and Left Paddle 1 and 2. The Vader series C and Z buttons and the Apex 5 and Apex 6 shoulder macro buttons map as Misc 2 and Misc 3, and the Vader 5 Pro's three extra buttons as Misc 4 to 6. The Apex 5, Apex 6, Vader 3 Pro, Vader 4 Pro and Vader 5 Pro report gyro and accelerometer.

### Other SDL drivers (24 USB identities)

These pads are claimed by SDL's dedicated drivers by USB identity, not through its controller list, the way the Flydigi driver works. The names follow SDL's driver code and its USB ID list. SDL gives the 8BitDo Ultimate 3, the 8BitDo Ultimate 2C Wireless and the two EVOTOP DirectInput identities no name of its own, so they show the pad's USB product name.

| Identity | Device | SDL driver |
| --- | --- | --- |
| **2DC8:202F** | 8BitDo Ultimate 3, mode switch on BT | 8BitDo |
| **2DC8:301B** | 8BitDo Ultimate 2C Wireless, mode switch on BT | 8BitDo |
| **3537:10B8** | GameSir G7 Pro 8K, wired, 2.4 GHz or Bluetooth in 8K mode | GameSir |
| **3537:103C** | GameSir Tarantula 8K, wired, 2.4 GHz or Bluetooth | GameSir |
| **1949:0419** | Amazon Luna Controller over Bluetooth | Luna |
| **18D1:9400** | Google Stadia Controller | Stadia |
| **0955:7214** | NVIDIA SHIELD Controller, v1.04 | SHIELD |
| **057E:2017** | Nintendo SNES Controller (Switch Online) | Switch |
| **057E:2019** | Nintendo N64 Controller (Switch Online) | Switch |
| **057E:201E** | Nintendo SEGA Genesis Controller (Switch Online) | Switch |
| **057E:200E** | Nintendo Switch Joy-Con charging grip, with its Joy-Cons over USB | Switch |
| **057E:0306** | Wii Remote | Wii |
| **057E:0330** | Wii Remote Plus | Wii |
| **33DD:0006** | ZUIKI MASCON PRO | ZUIKI |
| **33DD:0017** | ZUIKI EVOTOP, PC mode over Bluetooth | ZUIKI |
| **33DD:001C** | ZUIKI EVOTOP, UWB receiver in DirectInput mode | ZUIKI |
| **33DD:001D** | ZUIKI EVOTOP, PC mode in DirectInput | ZUIKI |
| **33DD:0020** | ZUIKI EVOTOP AXIS, DirectInput mode | ZUIKI |
| **2E8A:10C6** | Any SInput device, generic identity | SInput |
| **2E8A:10DD** | HHL GC Ultimate | SInput |
| **2E8A:10DF** | HHL ProGCC | SInput |
| **2E8A:10E0** | Bonziri FireBird | SInput |
| **2E8A:10E5** | Void Gaming PS4 FireBird | SInput |
| **38D2:1014** | Void Gaming Void GENESIS | SInput |

SDL's Wii driver recognizes a Wii U Pro Controller by the extension it reports, under either Wii identity.

### Other (3)

| Vendor | Devices |
| --- | --- |
| **DragonRise** | DragonRise Generic USB PCB, sometimes configured as a PC Twin Shock Controller |
| **Steam** | Steam Virtual Gamepad |
| **Streaming** | Streaming mobile touch virtual controls |

### With a shipped mapping (464)

Pads carrying a mapping in the database, so their buttons and axes land in the right places
the moment they are plugged in. SDL's database holds 248 names in its Windows section, the
community SDL_GameControllerDB that PadForge's SDL3 build adds holds 214 more, and PadForge
adds two of its own, for the DualShock 3 under DsHidMini and the PS VR Aim Controller.

| Vendor | Devices |
| --- | --- |
| **8BitDo** | 8BitDo 64 Bluetooth Controller, 8BitDo Adapter 2, 8BitDo Dogbone, 8BitDo F30, 8BitDo F30 Arcade Joystick, 8BitDo F30 Arcade Stick, 8BitDo FC30 Pro, 8BitDo GameCube, 8BitDo Lite 2, 8BitDo Lite SE, 8BitDo M30, 8BitDo M30 Gamepad, 8BitDo Micro gamepad, 8BitDo N30, 8BitDo N30 Pro 2, 8BitDo N64, 8BitDo NEOGEO, 8BitDo NES30, 8BitDo NES30 Gamepad, 8BitDo NES30 Pro, 8BitDo P30, 8BitDo Pro 2, 8BitDo Receiver, 8BitDo S30, 8BitDo SF30, 8BitDo SF30 Pro, 8BitDo SFC30, 8BitDo SFC30 Gamepad, 8BitDo SN30, 8BitDo SN30 Gamepad, 8BitDo SN30 Pro, 8BitDo SN30 Pro+, 8BitDo SNES30 Gamepad, 8BitDo Ultimate, 8BitDo Ultimate 2C, 8BitDo Ultimate 2C Wireless, 8BitDo Ultimate C, 8BitDo Ultimate Wired Controller, 8BitDo Ultimate Wireless Controller, 8BitDo Xbox One SN30 Pro, 8BitDo Zero 2, 8BitDo Zero Gamepad |
| **HORI** | HORI Fighting Commander, Hori Fighting Commander 4 (PS3), Hori Fighting Commander 4 (PS4), Hori Fighting Stick Mini 3, HORI Fighting Stick mini 4 (PS3), HORI Fighting Stick mini 4 (PS4), Hori Pad 3, Hori Pad 3 Turbo, Hori Pad A, Hori Pokken Tournament DX Pro Pad, Horipad, HORIPAD 4 (PS3), HORIPAD 4 (PS4), HORIPAD mini4, REAL ARCADE PRO.3, Real Arcade Pro.4, REAL ARCADE PRO.4 VLX, REAL ARCADE Pro.V3, Real Arcade Pro.V4 |
| **Mad Catz** | Mad Catz C.T.R.L.R, Mad Catz FightPad PRO (PS3), Mad Catz FightPad PRO (PS4), Mad Catz FightStick TE S+ (PS3), Mad Catz FightStick TE S+ (PS4), Mad Catz FightStick TE2+ PS3, Mad Catz FightStick TE2+ PS4, Mad Catz Micro C.T.R.L.R, Mad Catz TE2 PS3 Fightstick, Mad Catz TE2 PS4 Fightstick, Madcatz Arcade Fightstick TE S PS3, Madcatz Arcade Fightstick TE S+ PS3, MadCatz SFIV FightStick PS3 |
| **Saitek** | Saitek Cyborg, Saitek Cyborg V.1 Game pad, Saitek Dual Analog Pad, Saitek P220, Saitek P2500 Force Rumble Pad, Saitek P2600, Saitek P2900, Saitek P480 Rumble Pad, Saitek P990, Saitek P990 Dual Analog Pad, Saitek PS1000, Saitek PS2700, Saitek Rumble Pad |
| **Raphnet** | Raphnet 3DO Adapter, Raphnet Dreamcast Adapter, Raphnet GameCube Adapter, Raphnet GC and N64 Adapter, Raphnet Jaguar Adapter, Raphnet N64 Adapter, Raphnet NES Adapter, Raphnet PlayStation Adapter, Raphnet Saturn, Raphnet SNES Adapter, Raphnet Vectrex Adapter, Raphnet Wii Classic Adapter |
| **Logitech** | Logitech ChillStream, Logitech Cordless Precision, Logitech Cordless Wingman, Logitech Dual Action, Logitech F510 Gamepad, Logitech F710 Gamepad, Logitech Precision Gamepad, Logitech WingMan, Logitech WingMan Action Pad, Logitech WingMan RumblePad |
| **Mayflash** | Mayflash Arcade Stick, Mayflash F101, Mayflash F300 Elite Arcade Joystick, Mayflash Magic NS, Mayflash N64 Adapter, Mayflash N64 Controller Adapter, Mayflash USB Adapter for original Sega Saturn controller, Mayflash Wii Classic Controller, Mayflash WiiU Pro Game Controller Adapter (DInput) |
| **Qanba** | Qanba 2, Qanba 2P, QanBa Arcade JoyStick 1008, QanBa Arcade JoyStick 4018, Qanba Dragon Arcade Joystick, QanBa Joystick Plus, QanBa Joystick Q4RAF, Qanba Obsidian Arcade Joystick (PS3), Qanba Obsidian Arcade Joystick (PS4) |
| **Sanwa** | Sanwa 4Button, Sanwa Easy Grip, Sanwa Micro Grip P3, Sanwa Micro Grip Pro, Sanwa Online Grip, Sanwa PlayOnline Mobile, Sanwa PlayStation Adapter, Sanwa Smart Grip II, Sanwa Virtua Grip |
| **GameSir** | GameSir, GameSir G3w, GameSir G4, GameSir G7 Pro, GameSir T4 Kaleid, GameSir T4 Pro, GameSir Tegenaria Lite, GameSir X5 Lite |
| **PowerA** | PowerA Fusion Nintendo Switch Arcade Stick, PowerA Fusion Pro Nintendo Switch Controller, PowerA OPS v1 Wireless Controller, PowerA OPS v3 Pro Wireless Controller, PowerA Pro Ex, PowerA PS3 Controller, PowerA Wired GameCube Controller |
| **Razer** | Razer Huntsman V3 Pro, Razer Hydra, Razer Panthera (PS3), Razer Panthera (PS4), Razer Raiju Mobile, Razer Raion Fightpad for PS4, Razer Serval |
| **Sony** | Sony DualShock 2, Sony DualShock 3, Sony DualShock 3 (DsHidMini SDF and SXS), Sony PlayStation Adapter, Sony PlayStation Portable, Sony PlayStation Vita, Sony PS VR Aim Controller |
| **Elecom** | Elecom DUX60 MMO, Elecom Gamepad, Elecom PlayStation Adapter, Elecom U1012, Elecom U3912T, Elecom U4113S |
| **Hyperkin** | Hyperkin Admiral N64 Controller, Hyperkin N64 Adapter, Hyperkin RetroN Sq, Hyperkin Scout, Hyperkin Scout Premium SNES Controller, Hyperkin Trooper 2 |
| **InterAct** | InterAct ActionPad, InterAct AxisPad, InterAct Hammerhead, InterAct Hammerhead FX, InterAct ProPad |
| **SteelSeries** | SteelSeries, SteelSeries Free, SteelSeries Nimbus Cloud, SteelSeries Stratus Duo, SteelSeries Stratus XL |
| **Thrustmaster** | Thrustmaster Dual Analog 4, Thrustmaster Dual Trigger 3-in-1, ThrustMaster eSwap PRO Controller, Thrustmaster Firestorm Dual Power, Thrustmaster Firestorm Dual Power 3 |
| **Betop** | Betop 2126F, Betop BFM Gamepad, Betop Controller, Betop Gamepad |
| **Dual** | Dual Box WII, Dual Plus PlayStation Adapter, Dual Power 3, Dual USB Vibration Joystick |
| **Genius** | Genius, Genius Maxfire Blaze 3, Genius Maxfire Grandias 12, Genius MaxFire Grandias 12V |
| **PDP** | Afterglow PS3 Controller, PDP Versus Fighting Pad, Rock Candy PS3 Controller, Victrix Pro Fight Stick for PS4 |
| **Sega** | Sega Genesis Mini 3B Controller, Sega Mega Drive Mini 6B Controller, Sega Multi Controller, Sega Saturn Controller |
| **Trust** | Trust 850F, Trust Gamepad, Trust Predator GM1200, Trust Sight Fighter |
| **USB** | USB 4-Axis 12-Button Gamepad, USB Controller, USB Gamepad, USB Vibration Joystick (BM) |
| **Firestorm** | Firestorm, Firestorm 2, Firestorm D3 |
| **GameStop** | GameStop, GameStop Gamepad, GameStop PS4 Fun Controller |
| **Gioteck** | Gioteck, Gioteck PS3 Controller, Gioteck VX2 Controller |
| **Microsoft** | Microsoft Dual Strike, Microsoft SideWinder, Microsoft SideWinder Plug and Play |
| **Rockfire** | Rockfire CosmoVoyager, Rockfire MaxFire G08XU, Rockfire Space Ranger |
| **ROG** | ROG Chakram, ROG Chakram Core, ROG Chakram X |
| **Anbernic** | Anbernic Game Pad, Anbernic RG P01 |
| **Defender** | Defender Game Racer X7, Defender Joystick Cobra R4 |
| **EMS** | EMS Production PS2 Adapter, EMS TrioLinker Plus II |
| **EXEQ** | EXEQ, EXEQ RF USB Gamepad 8206 |
| **Flydigi** | Flydigi Apex, Flydigi Vader 2 |
| **Game** | Game Controller for PC, Game VIB Joystick |
| **Gravis** | Gravis Destroyer Tilt, Gravis Eliminator Pro |
| **iBuffalo** | iBuffalo AC02 Arcade Joystick, iBuffalo SNES Controller |
| **iBUFFALO** | iBUFFALO BSGP1204 Series, iBUFFALO BSGP1204P Series |
| **iDroidCon** | iDroidCon, iDroidCon Controller |
| **Ipega** | Ipega PG-9023, Ipega PG9087 |
| **MOGA** | MOGA XP5-A Plus, MOGA XP5-X Plus |
| **NACON** | NACON GC-400ES, Nacon GC101 1.03 |
| **NES** | NES Adapter, NES Controller |
| **Nintendo** | Nintendo GameCube Controller, Nintendo Retrolink USB Super SNES Classic Controller |
| **Nintendo Switch** | Nintendo Switch, Nintendo Switch Pro Controller |
| **Pro** | Pro Elite PS3 Controller, Pro Ex mini PS3 Controller |
| **PS** | PS Controller, PS to USB convert cable |
| **PS3** | PS3 Controller, PS3 RF pad |
| **Retro** | Retro Bit Sega Genesis Adapter, Retro Fighters D6 |
| **Retrolink** | Retrolink Sega Saturn Classic Controller, Retrolink SNES Controller |
| **RetroUSB.com** | RetroUSB.com RetroPad, RetroUSB.com Super RetroPort |
| **Revolution** | Revolution Pro Controller, Revolution Pro Controller 3 |
| **Super** | Super Famicom Controller, Super Racer |
| **Taito** | Taito Egret II Mini Control Panel, Taito Egret II Mini Controller |
| **TigerGame** | TigerGame PlayStation Adapter, TigerGame PS/PS2 Game Controller Adapter |
| **Tomee** | Tomee NES Adapter, Tomee SNES Adapter |
| **Xiaomi** | Xiaomi Black Shark (L), Xiaomi XMGP01YM |
| **3** | 3 In 1 Conversion Box |
| **3DRUDDER** | 3DRUDDER |
| **4Play** | 4Play Adapter |
| **Acme** | Acme GA-02 |
| **Acrux** | Acrux |
| **Acteck** | Acteck AGJ-3200 |
| **ADT1** | ADT1 |
| **Airflo** | Airflo PS3 Controller |
| **Alienware** | Alienware Dual Compatible PlayStation Controller |
| **Amazon** | Amazon Luna Controller |
| **Aquaplus** | Aquaplus Piece |
| **Arcade** | Arcade |
| **ASCII** | ASCII Seamic Controller |
| **Astro** | Astro City Mini |
| **ASUS** | ASUS ROG Kunai 3 Gamepad |
| **Atari** | Atari CX Controller |
| **AtGames** | AtGames Legends Gamer Pro |
| **Backbone** | Backbone One |
| **Batarang** | Batarang |
| **Battalife** | Battalife Joystick |
| **Battlefield** | Battlefield 4 PS3 Controller |
| **BDA** | BDA PS4 Fightpad |
| **Belkin** | Belkin Nostromo N40 |
| **Bigben** | Bigben PS3 Controller |
| **BrutalLegendTest** | BrutalLegendTest |
| **BUFFALO** | BUFFALO BSGP1601 Series |
| **Capcom** | Capcom Home Arcade Controller |
| **Cideko** | Cideko AK08b |
| **Competition** | Competition Pro |
| **Cthulhu** | Cthulhu |
| **Cyber** | Cyber Gadget GameCube Controller |
| **Cyborg** | Cyborg V.3 Rumble Pad |
| **DA** | DA Leader |
| **Datel** | Datel Arcade Joystick |
| **EA** | EA SPORTS PS3 Controller |
| **Easy** | Easy Grip |
| **Eliminator** | Eliminator AfterShock |
| **ESM** | ESM 9110 |
| **Essential** | Essential |
| **FC30** | FC30 Pro |
| **FC801** | FC801 |
| **FF-GP1** | FF-GP1 |
| **FIGHTING** | FIGHTING STICK V3 |
| **Gamecube** | Gamecube Controller |
| **GameCube** | GameCube Controller |
| **GAMEPAD** | GAMEPAD 3 TURBO |
| **Gamepad** | Gamepad Pro USB |
| **Gamesir-G5** | Gamesir-G5 |
| **GameSir-T3** | GameSir-T3 2.02 |
| **Gametel** | Gametel GT004 01 |
| **Gamo2** | Gamo2 Divaller |
| **GGE909** | GGE909 Recoil Pad |
| **Google** | Google Stadia Controller |
| **GT2a** | GT2a |
| **Hama** | Hama Scorpad |
| **Hatsune** | Hatsune Miku Sho Controller |
| **Havit** | Havit HV G60 |
| **HitBox** | HitBox Edition Cthulhu+ |
| **HJD-X** | HJD-X |
| **HRAP2** | HRAP2 on PS/SS/N64 Joypad to USB BOX |
| **HuiJia** | HuiJia SNES Controller |
| **HyperX** | HyperX Clutch |
| **iGUGU** | iGUGU Gamecore |
| **Impact** | Impact Black |
| **INJUSTICE** | INJUSTICE FightStick PS3 Controller |
| **IPEGA** | IPEGA |
| **JC-P301U** | JC-P301U |
| **JC-U3613M** | JC-U3613M (DInput) |
| **JC-W01U** | JC-W01U |
| **Joypad** | Joypad Alpha Shock |
| **Joytech** | Joytech JS-112 |
| **JPD** | JPD FFB |
| **JYS** | JYS Adapter |
| **KADE** | KADE |
| **Keio** | Keio |
| **KidzPlay** | KidzPlay Adventure PlayStation Controller |
| **King** | King PS3 Controller |
| **Leadership** | Leadership |
| **Logic3** | Logic3 |
| **M64** | M64 Pro Controller |
| **Macally** | Macally |
| **MADCATZ** | MADCATZ SFV Arcade FightStick Alpha PS4 |
| **Matricom** | Matricom |
| **MaxJoypad** | MaxJoypad Virtual Controller |
| **Mega** | Mega Drive Controller |
| **Miller** | Miller Lite Cantroller |
| **MLG** | MLG Gamepad PS3 Controller |
| **Mobapad** | Mobapad Chitu HD |
| **Monect** | Monect Virtual Controller |
| **MP-8866** | MP-8866 Super Dual Box |
| **MUSIA** | MUSIA PlayStation 2 Input Display |
| **N64** | N64 Adaptoid |
| **Nebular** | Nebular |
| **NeoGeo** | NeoGeo X Arcade Stick |
| **NEXT** | NEXT SNES Controller |
| **NGDS** | NGDS |
| **Nostromo** | Nostromo N45 |
| **NVIDIA** | NVIDIA Virtual Gamepad |
| **Nyko** | Nyko Playpad |
| **NYKO** | NYKO AIRFLO EX |
| **Oklick** | Oklick W-2 |
| **Onlive** | Onlive Wireless Controller |
| **OPP** | OPP PS3 Controller |
| **Orange** | Orange Controller |
| **OrangeFox86** | OrangeFox86 DreamPicoPort |
| **OUYA** | OUYA Game Controller |
| **P4** | P4 Wired Gamepad |
| **Piranha** | Piranha xtreme |
| **PlaySega** | PlaySega |
| **PS1** | PS1 Controller |
| **PS2** | PS2 Controller |
| **PS360+** | PS360+ v1.66 |
| **PS4** | PS4 Controller |
| **PS5** | PS5 Controller |
| **PSX** | PSX |
| **QANBA** | QANBA DRONE ARCADE JOYSTICK |
| **R1** | R1 Mobile Controller |
| **RadioShack** | RadioShack |
| **Ramox** | Ramox FPS Controller |
| **Retrode** | Retrode Adapter |
| **RetroUSB** | RetroUSB N64 RetroPort |
| **Revenger** | Revenger |
| **Rumble** | Rumble Force |
| **run'n'drive** | run'n'drive |
| **RX** | RX Gamepad |
| **Samsung** | Samsung EIGP20 |
| **Satechi** | Satechi Controller |
| **Saturn_Adapter_2.0** | Saturn_Adapter_2.0 |
| **Score** | Score A |
| **Scuf** | Scuf PS4 Controller |
| **SFX** | SFX |
| **Shogun** | Shogun Bros Chameleon X1 |
| **SL-6555-SBK** | SL-6555-SBK |
| **SL-6566** | SL-6566 |
| **SNES** | SNES Controller |
| **SPEEDLINK** | SPEEDLINK STRIKE Gamepad |
| **SpeedLink** | SpeedLink Strike FX |
| **Speedlink** | Speedlink Torid |
| **SplitFish** | SplitFish Game Controller |
| **Steam** | Steam Virtual Gamepad |
| **STK-7024X** | STK-7024X |
| **SVEN** | SVEN X-PAD |
| **SZMY-POWER** | SZMY-POWER PC Gamepad |
| **T** | T Mini Wireless |
| **TE** | TE Kitty |
| **Team** | Team 5 |
| **Techmobility** | Techmobility X6-38V |
| **Technology** | Technology Innovation PS2 Adapter |
| **Tencent** | Tencent Xianyou Gamepad |
| **THEC64** | THEC64 Joystick |
| **THEGamepad** | THEGamepad |
| **ThundeRobot** | ThundeRobot G30 |
| **Tournament** | Tournament PS3 Controller |
| **Tronsmart** | Tronsmart |
| **TWCS** | TWCS Throttle |
| **Twin** | Twin Shock |
| **TwinShock** | TwinShock PS2 |
| **Uniplay** | Uniplay U6 |
| **uRage** | uRage Gamepad |
| **V5** | V5 Game Pad |
| **Venom** | Venom Arcade Joystick |
| **Void** | Void Gaming Void GENESIS |
| **XEOX** | XEOX Gamepad SL-6556-BK |
| **Xeox** | Xeox |
| **XiaoMi** | XiaoMi Game Controller |
| **Xin-Mo** | Xin-Mo Dual Arcade |
| **Xterminator** | Xterminator Digital Gamepad |
| **ZD-T** | ZD-T Android |
| **ZENAIM** | ZENAIM ARCADE CONTROLLER |
| **ZEROPLUS** | ZEROPLUS P4 Wired Gamepad |

---

## Racing wheels (67)

**Driven in the wheel's own protocol**, with rotation range, autocenter and the LED strip on
the wheels that have them: the Logitech, Thrustmaster and Fanatec models. Everything else is
recognized as a wheel and takes force feedback through the standard path. See
[Force Feedback](../features/force-feedback.md).

| Vendor | Devices |
| --- | --- |
| **Logitech** | Logitech Driving Force GT, Logitech Driving Force Pro, Logitech G25, Logitech G27, Logitech G29, Logitech G920, Logitech G923, Logitech G923 for Playstation 4 and PC, Logitech generic wheel, Logitech Momo Force, Logitech Momo Racing, Logitech PRO Racing Wheel, Logitech PRO Racing Wheel for Xbox, Logitech Speed Force Wireless, Logitech WingMan Formula Force |
| **Fanatec** | Fanatec ClubSport Wheel Base V1, Fanatec ClubSport Wheel Base V2, Fanatec ClubSport Wheel Base V2.5, Fanatec CSL Elite, Fanatec CSL Elite Wheel Base+, Fanatec Forza Motorsport, Fanatec generic wheel / CSL DD / GT DD Pro, Fanatec Podium Wheel Base DD1, Fanatec Podium Wheel Base DD2, Fanatec Porsche Wheel |
| **Thrustmaster** | Thrustmaster Motor Sport GT, Thrustmaster T150, Thrustmaster T248, Thrustmaster T300RS, Thrustmaster T500RS, Thrustmaster TMX, Thrustmaster TS-XW, Thrustmaster TX, Thrustmaster Wheel FFB |
| **Padix** | Padix Force Feedback Wheel, Padix TW6 Wheel, Padix USB Wheel, Padix USB Wireless 2.4GHz Wheel, Padix USB Wireless 2.4GHz Wheelpad, Padix Vibration USB Wheel |
| **MOZA** | Moza R12, Moza R16/R21, Moza R3, Moza R5, Moza R9 |
| **Asetek SimSports** | Asetek SimSports Forte, Asetek SimSports Invicta, Asetek SimSports La Prima, Asetek SimSports Tony Kannan |
| **Simucube** | Simucube 1, Simucube 2 Pro, Simucube 2 Sport, Simucube 2 Ultimate |
| **AVB** | AVB Mag Turbo Force, AVB Top Shot Force Feedback Racing Wheel |
| **Cammus** | Cammus C12, Cammus C5 |
| **Guillemot** | Guillemot Force Feedback Racing Wheel, Guillemot Race Leader Force Feedback |
| **ACT** | ACT LABS Force RS |
| **DragonRise** | DragonRise Wired Wheel |
| **Generic** | Generic FFBoard OpenFFBoard universal forcefeedback wheel |
| **PXN** | PXN VD6 |
| **Saitek** | Saitek R440 Force Wheel |
| **Simagic** | Simagic |
| **VRS** | VRS DirectForce Pro |
| **Xbox 360** | Xbox 360 Wireless Racing Wheel |

**MOZA, both generations.** Each MOZA base has two USB product IDs, one per hardware revision.
PadForge's SDL fork carries the second-generation IDs (R3 0015, R5 0014, R9 0012, R12 0016, R16/R21 0010,
under vendor 346E) alongside the originals, so a newer base is typed as a wheel and gets the Wheel tab.

**Pedals.** Fanatec ClubSport V3, CSL Elite, CSL Loadcell and CSL Loadcell V2, each with its
own rumble output. Pedal sets that enumerate separately are read as their own device, so they
feed a slot alongside the wheel.

---

## Flight controls

### Sticks (23)

| Vendor | Devices |
| --- | --- |
| **Padix** | Padix MetalStrike ForceFeedback, Padix MetalStrike Pro, Padix QF-688uv Windstorm Pro, Padix QF-707u Bazooka, Padix USB joystick with viewfinder, Padix USB vibration joystick with viewfinder, Padix USB Wireless 2.4GHz, Padix USB Wireless 2.4GHZ, Padix Wireless MetalStrike |
| **Guillemot** | Guillemot Jet Leader 3D, Guillemot Jet Leader Force Feedback |
| **Logitech** | Logitech Extreme 3D, Logitech WingMan Force |
| **Thrustmaster** | HOTAS Warthog Joystick, ThrustMaster T.16000M Joystick |
| **VIRPIL Controls** | VIRPIL Controls L-VPC Stick MT-50CM3, VIRPIL Controls R-VPC Stick MT-50CM3 |
| **VKB** | Gunfighter Mk.III 'Space Combat Edition', VKB Gladiator NXT Evo |
| **AVB** | AVB Top Shot Pegasus |
| **Saitek** | Saitek Pro Flight X-56 Rhino Stick |
| **Turtle Beach** | Turtle Beach VelocityOne |
| **Yawman** | Yawman Arrow |

### Throttles (4)

| Vendor | Devices |
| --- | --- |
| **Saitek** | Saitek Pro Flight X-56 Rhino Throttle |
| **Thrustmaster** | HOTAS Warthog Throttle |
| **Turtle Beach** | Turtle Beach VelocityOne Throttle |
| **VIRPIL Controls** | VIRPIL Controls VPC VMAX Prime Throttle |

A stick, a throttle and a set of pedals each read as their own device and can feed one virtual
controller together, so a button on the throttle chords with a button on the stick.

---

## Arcade sticks (30)

| Vendor | Devices |
| --- | --- |
| **HORI** | Hori Fighting Stick Alpha in PC Mode, Hori Fighting Stick Alpha in PS4 Mode, Hori Fighting Stick Alpha in PS5 Mode, Hori Fighting Stick mini 4 kai, Hori Real Arcade Pro 4, HORI Real Arcade Pro 4, Hori Real Arcade Pro Hayabusa Xbox One, HORI Real Arcade Pro V Hayabusa in Switch Mode, Hori Real Arcade Pro V Kai 360, Hori Real Arcade Pro V Kai Xbox One, Hori Real Arcade Pro VX, Hori Real Arcade Pro VX-SA, Hori Real Arcade Pro. EX, Hori Real Arcade Pro.EX, Hori Real Arcade Pro.EX Premium VLX, Hori Real Arcade Pro.VX SA, Real Arcade Pro 4 |
| **Qanba** | Qanba Dragon Arcade Joystick in PC Mode, Qanba Dragon Arcade Joystick in PS3 Mode, Qanba Dragon Arcade Joystick in PS4 Mode, Qanba Obsidian Arcade Joystick in PC Mode, Qanba Obsidian Arcade Joystick in PS3 Mode, Qanba Obsidian Arcade Joystick in PS4 Mode |
| **Hitbox** | Hitbox Arcade Stick |
| **Mad Catz** | Street Fighter IV Arcade Stick TE - Chun Li |
| **NACON** | NACON Daija Arcade Stick |
| **PDP** | PDP Versus Fighting Pad |
| **PowerA** | PowerA Nintendo Switch Fusion Arcade Stick |
| **Razer** | Razer Atrox Arcade Stick |
| **Venom** | Venom Arcade Stick |

---

## GameCube adapters (8)

| Vendor | Devices |
| --- | --- |
| **Austgame** | Austgame GameCube to USB convertor |
| **Cyber** | Cyber Gadget GameCube Controller |
| **DragonRise** | DragonRise GameCube Controller Adapter |
| **GameCube** | GameCube \{HuiJia USB box\} |
| **Nintendo** | Nintendo Wii U GameCube Controller Adapter |
| **Nintendo Switch** | Nintendo Switch 2 NSO GameCube Controller |
| **PDP** | PDP Wired Fight Pad Pro for Nintendo Switch |
| **PowerA** | PowerA Wired Controller Nintendo GameCube Style |

---

## Devices PadForge's own code claims (24 USB identities)

SDL lists none of these. PadForge recognizes each one itself and drives the part SDL cannot. The 3Dconnexion models below were sold under Logitech's vendor ID. PadForge also reads every device on 3Dconnexion's own vendor ID, 256F, that reports the multi-axis controller usage, so current SpaceMouse models need no entry here.

| Identity | Device | What PadForge adds |
| --- | --- | --- |
| **046D:C293** | Logitech WingMan Formula Force GP | Force feedback in the wheel's own protocol, fixed 180-degree range |
| **044F:B689** | Thrustmaster TS-PC Racer | Force feedback in the wheel's own protocol |
| **0EB7:183B** | Fanatec ClubSport Pedals V3 | Pedal rumble on both motors |
| **0EB7:6204** | Fanatec CSL Elite Pedals | Pedal rumble on both motors |
| **0EB7:6205** | Fanatec CSL Pedals Loadcell | Pedal rumble on both motors |
| **0EB7:6206** | Fanatec CSL Pedals LC V2 | Pedal rumble on both motors |
| **054C:03D5** | PlayStation Move over Bluetooth | Pairing and input, see [PlayStation Move](ps-move.md) |
| **054C:0C5E** | PlayStation Move ZCM2 over USB | Input, see [PlayStation Move](ps-move.md) |
| **054C:042F** | PlayStation Navigation controller | Pairing and input |
| **0583:B047** | Buffalo BSGC101 (one PlayStation port) | Rumble on the PS1 or PS2 pad behind the converter |
| **0583:B048** | Buffalo BSGC201 (two PlayStation ports) | Rumble on the PS1 or PS2 pads behind the converter |
| **05C6:9244** | Xbox 360 wireless receiver, a clone | Windows' own Xbox 360 driver, which PadForge binds |
| **046D:C603** | SpaceMouse Plus XT | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C605** | CadMan | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C606** | SpaceMouse Classic | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C621** | Spaceball 5000 | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C623** | Space Traveler | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C625** | Space Pilot | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C626** | Space Navigator | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C627** | Space Explorer | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C628** | Space Navigator for Notebooks | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C629** | Space Pilot Pro | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C62B** | SpaceMouse Pro | All six axes, see [SpaceMouse](spacemouse.md) |
| **046D:C640** | NuLOOQ | All six axes, see [SpaceMouse](spacemouse.md) |

## Handheld PCs

There is no model table. PadForge learns a handheld's hidden buttons on the machine, from the
keystrokes, vendor HID report bits and firmware WMI events the press produces, so a handheld that
ships tomorrow needs no release. The code names the shapes it has been tuned on and the vendor
tools it watches for.

| What the code names | Where it applies |
| --- | --- |
| Lenovo Legion Go (report byte and Win+D on one button), Legion Pro 7 laptop (Vantage and Smart Connect keys over WMI) | Report fields, key combinations, system events |
| ASUS ROG Ally (a code that appears only while the key is down) | Report fields |
| GPD Win 5 (a flag byte whose flags rise together) | Report fields |
| Zotac handhelds (the wheels) | Report fields |
| Vendor tools detected while running: Legion Space, Armoury Crate, MSI Center M, Zotac quick settings, AYASpace | The Hidden Buttons row says which one still reacts to the same buttons |

The Steam Deck needs none of this. Its paddles and motion sensor arrive through SDL3 like any other
Steam controller. See [Handheld PC Buttons](../features/handheld-buttons.md).

---

## Specialty and legacy controllers

Windows gives none of these usable input on its own. Some have no Windows driver, some get one that reads nothing, and some speak a protocol only their makers' discontinued software knew. PadForge reads them through its SDL3 build, most with no setup step. The PlayStation Move accessories are the exception: PadForge's own Move reader decodes them.

### Plug in over USB

PadForge binds the driver each of these needs a few seconds after it appears. See [Driver Management](../features/driver-management.md#controllers-windows-leaves-without-a-driver).

| Device | Identity | Notes |
| --- | --- | --- |
| **Namco GunCon 2** | 0B9A:016A | Needs a CRT with composite sync. The picker names its aim **Gun Aim X** and **Gun Aim Y**. Calibrate it from its card on the Devices page. The EMS LCD TopGun shares the ID. |
| **Taito Densha de GO! Type 2, Shinkansen and Ryojohen controllers** | 0AE4:0004, 0AE4:0005, 0AE4:0007 | Brake on the left trigger, power on the right |
| **Multi Train Controller, Train Mascon** | 0AE4:0101, 1C06:77A7 | The lever on the left stick, the reverser on the right stick |
| **I-Force wheels and joysticks** | 14 IDs | Thrustmaster Motor Sport GT, Logitech WingMan Force and WingMan Formula Force, AVB Top Shot Pegasus, Mag Turbo Force and Top Shot Force Feedback Racing Wheel, ACT LABS Force RS, Saitek R440 Force Wheel, and the Guillemot Race Leader, Jet Leader, Jet Leader 3D and Force Feedback Racing Wheel. Force feedback through the standard path. |
| **Original Xbox controllers** | Class 0x58, and 63 IDs by name | Pads, wheels, dance pads and light guns, through a passive Xbox-to-USB cable. On a controller with one of the 63 listed IDs, the pressure of A, B, X, Y, White and Black fills the [button pressure](../features/mappings.md#button-pressure) rows. Any other original Xbox controller reports the same pressures, and you record them into those rows yourself. |
| **Capcom Steel Battalion controller** | 0A7B:D000 | 9 axes and 46 buttons. The lamps stay off. |
| **Xbox 360 Big Button receiver** | 045E:02A0 | Four pads |
| **Gametrak** | 14B7:0982 | 6 axes, 12 buttons and a hat |
| **DJI RC (RM330)** | 2CA3:1023 | Sticks and dials. Over USB it reports no buttons. |
| **Namco USIO** | 0B9A:0910, 0B9A:0900 | Two Taiko no Tatsujin drums, or four Tekken arcade sticks. Switch the layout from the board's cards on the Devices page. |
| **Konami P3IO** | 1CCF:8008 | Two dance pads, DanceDanceRevolution SuperNova 2 and X |
| **Konami P4IO** | 1CCF:8010 | jubeat and DanceDanceRevolution White, 32 buttons |
| **CH Products Multi-Function Panel** | 068E:00F0 | 102 buttons |
| **Ergodex DX1** | 1603:0002 | 52 buttons |
| **NaturalPoint TrackIR 2, TrackIR 3** | 131D:0150, 131D:0155 | Three axes. A TrackIR on NaturalPoint's driver stays there. |
| **Tacx T1904, T1932 trainer head units** | 3561:1904, 3561:1932 | 5 axes and 4 buttons |

### Plug in, Windows reads it and PadForge decodes it

| Device | Identity | Notes |
| --- | --- | --- |
| **Logitech Speed Force Wireless (Wii)** | 046D:C29C | Wheel, two pedals, 11 buttons. No force feedback. |
| **PhoenixRC USB adapter** | 1781:0898 | 8 axes |
| **Microsoft SideWinder Game Voice** | 045E:003B | 8 buttons |
| **P5 Glove** | 0D7F:0100 | 5 finger axes, 4 buttons |
| **Dream Cheeky Roll-Up Drum Kit** | 1941:8021 | 6 pads. A weather station and a missile launcher share the ID and read as the drum kit. |
| **OCZ Neural Impulse Actuator** | 1234:0000 | 1 axis |
| **Oculus Rift DK1 head tracker** | 2833:0001 | Yaw, pitch and roll as axes, plus gyro and accelerometer |
| **Guitar Hero Live dongles** | 12BA:074B, 1430:07BB, 1430:079B | PS3 and Wii U, PS4, and Xbox One. The Xbox One dongle needs Microsoft's GameInput runtime on the PC. |
| **Rock Band 3 Pro keyboard, Mustang guitar and MIDI Pro Adapter** | 12BA:2330 to 2538 and 1BAD:3330 to 3538, six each | The PS3 and Wii models. A Squier guitar plays through the adapter. The Xbox 360 models read through XInput. |
| **THQ uDraw GameTablet for PS3** | 20D6:CB17 | Pen, buttons and accelerometer |
| **Top Shot Elite, Top Shot Fearmaster** | 12BA:04A0, 12BA:04A1 | Light guns for PS3 |
| **Tony Hawk RIDE and SHRED boards** | 12BA:0400, 1430:0100 | PadForge reads one axis each from the nose and tail accelerometers. The board's encrypted accelerometer data is not read. A board shows up only while it is switched on. |

### Switch drivers on the Devices page

Moving these to PadForge's driver costs Windows something, so they move only when you ask. Each device gets its own button on the Devices page, such as **Read the Chatpad**, and a dialog states the cost before **Switch Driver** confirms the move. See [driver switching](../features/devices.md#switch-driver-buttons).

| Device | What PadForge adds |
| --- | --- |
| **Xbox 360 chatpad** | Its keys, on a wired pad of revision 1.10 or 1.14 or through Microsoft's wireless receiver |
| **Xbox 360 uDraw GameTablet** | Pen and buttons, through Microsoft's wireless receiver |
| **Intel Wireless Series base station** | Its eight gamepads |
| **Creative Prodikeys PC-MIDI** | The music keys |
| **Logitech iFeel Mouse and iFeel MouseMan** | Rumble on the mouse's motor |

### Xbox 360 receivers Windows leaves without a driver

Clone Xbox 360 wireless receivers (045E:0291, 045E:02A9, 05C6:9244) and the Guitar Hero Live Xbox 360 dongle (1430:070B) get Windows' own Xbox 360 driver from PadForge, and then work in every game through XInput, with PadForge running or not.

### Bluetooth LE

PadForge connects to each of these in range that advertises. Pair a Daydream or an Oculus Go controller in Windows Settings first.

| Device | Notes |
| --- | --- |
| **Poke Ball Plus** | Press the top button to wake it. Its motion is not read. |
| **Google Daydream controller** | Touchpad as the left stick, gyro and accelerometer. Hold Home until the light pulses to wake it. |
| **Samsung Gear VR controller** | Touchpad as the left stick, gyro and accelerometer |
| **Oculus Go controller** | Touchpad as the left stick, no motion. Hold Oculus and Back until the light blinks to wake it. |
| **Guitar Hero Live guitar for iOS** | Whammy on the right stick's Y |
| **Zwift Play, Zwift Click** | Each half of a Play on firmware 1 is its own gamepad. Not the Zwift Ride or the Click v2. |
| **Thalmic Myo armband** | Five poses as buttons, roll, pitch and yaw as axes, gyro and accelerometer |

### Bluetooth, paired in Windows Settings

The PowerA MOGA in Mode A (Pocket, Pro, Pro Power, Hero Power), the Zeemote JS1 and JS1 H, the Chainpus BGP100 and the 2011 Phonejoy Digital and Analog. Windows may ask for PIN 1234 for a MOGA or a Phonejoy, and 0000 for a Zeemote JS1 H. The Windows Mixed Reality motion controllers and the SteelSeries Nimbus pair the same way. A WMR controller has to pair with the PC, not a headset, and one whose firmware Windows never updated may not start.

### Serial ports

Spaceballs, SpaceOrbs, Magellan pucks, the Gravis Stinger, the Logitech WingMan Warrior and CyberMan, RC transmitters, JVS arcade boards, VRinsight panels, Kettler ergometers, serial I-Force wheels with their force feedback, the Pony Canyon Master Controllers, DJI remotes and Konami's cabinet boards. Add each one from the pairing dialog. A DJI RC-N1 family remote on its bottom USB-C port needs no entry: PadForge opens its protocol port on its own once DJI's VCOM driver serves it. See [Pairing a controller](../features/devices.md#pairing-a-controller).

### Over the network

The DJI RC and DJI RC 2, on firmware from before DJI closed port 40007. Add each remote's IPv4 address from the pairing dialog. See [Pairing a controller](../features/devices.md#pairing-a-controller).

### Through another controller

| Device | Through | More |
| --- | --- | --- |
| **Guitar Hero guitars, World Tour and Band Hero drums, DJ Hero turntable, Taiko no Tatsujin TaTaCon, uDraw GameTablet, Drawsome tablet, Densha de GO! Shinkansen controller** | A Wii Remote's extension port. Not behind an active Motion Plus. | [Wii Controllers](wii-controllers.md) |
| **Ring-Con** | A right Joy-Con on its rail | [Ring-Con](wii-controllers.md#ring-con) |
| **PlayStation Move Sharp Shooter, Racing Wheel** | An original Move's EXT socket, over Bluetooth | [Sharp Shooter and Racing Wheel](ps-move.md#sharp-shooter-and-racing-wheel) |

### Keyboard protocol

The ION iCade cabinet (15E4:0132) reads as an arcade stick with eight buttons and a hat. A pad in iCade mode reads as a gamepad once you click **Read as iCade Controller** on its keyboard's card. The letters of both still reach the focused window. See [Pads in iCade mode](../features/devices.md#pads-in-icade-mode).

---

## RGB keyboards, mice and other lit devices (1,350) { #rgb-keyboards-mice-and-other-lit-devices }

PadForge lights these itself, over USB, with no maker's program needed: a color or an
effect, Screen Color, and key by key where the device's lights are known one by one. Each
takes the name its lighting family's own table gives it. 1,563 USB identities stand behind
the names, since a model often has more than one. See [Lighting](../features/lighting.md).

| Vendor | Devices |
| --- | --- |
| **Razer** | Razer Abyssus, Razer Abyssus 1800, Razer Abyssus 2000, Razer Abyssus Elite (D.Va Edition), Razer Abyssus Essential, Razer Abyssus V2, Razer Addressable RGB Controller, Razer Anansi, Razer Barracuda X Chroma Headset, Razer Base Station Chroma, Razer Base Station V2 Chroma, Razer Basilisk, Razer Basilisk Essential, Razer Basilisk Mobile (Receiver), Razer Basilisk Mobile (Wired), Razer Basilisk Ultimate, Razer Basilisk Ultimate (Wireless), Razer Basilisk V2, Razer Basilisk V3, Razer Basilisk V3 35K, Razer Basilisk V3 Pro (Wired), Razer Basilisk V3 Pro (Wireless), Razer Basilisk V3 Pro 35K (Wired), Razer Basilisk V3 Pro 35K (Wireless), Razer Basilisk V3 Pro 35K Phantom Green Edition (Wired), Razer Basilisk V3 Pro 35K Phantom Green Edition (Wireless), Razer Basilisk V3 X HyperSpeed, Razer Basilisk V4 Pro (Wired), Razer Basilisk V4 Pro (Wireless), Razer Basilisk X Hyperspeed, Razer BlackWidow (Classic), Razer BlackWidow 2019, Razer BlackWidow Chroma, Razer BlackWidow Chroma (Overwatch), Razer BlackWidow Chroma V2, Razer BlackWidow Elite, Razer BlackWidow Essential, Razer BlackWidow Lite, Razer BlackWidow Stealth Edition, Razer BlackWidow Tournament Edition 2014, Razer BlackWidow Tournament Edition Chroma, Razer BlackWidow Ultimate 2012, Razer BlackWidow Ultimate 2013, Razer BlackWidow Ultimate 2016, Razer BlackWidow V3, Razer BlackWidow V3 Mini HyperSpeed (Wired), Razer BlackWidow V3 Mini HyperSpeed (Wireless), Razer BlackWidow V3 Pro 2.4 Ghz Wireless, Razer BlackWidow V3 Pro Wired, Razer BlackWidow V3 TK, Razer BlackWidow V4, Razer BlackWidow V4 75%, Razer BlackWidow V4 Low Profile TKL (Wired), Razer BlackWidow V4 Low Profile TKL (Wireless), Razer Blackwidow V4 Low-profile, Razer Blackwidow V4 Low-profile Wireless, Razer BlackWidow V4 Mini HyperSpeed (Wired), Razer BlackWidow V4 Mini HyperSpeed (Wireless), Razer BlackWidow V4 Pro, Razer BlackWidow V4 Pro 75% (Wired), Razer BlackWidow V4 Pro 75% (Wireless), Razer BlackWidow V4 Tenkeyless HyperSpeed (Wired), Razer BlackWidow V4 Tenkeyless HyperSpeed (Wireless), Razer BlackWidow V4 X, Razer BlackWidow X Chroma, Razer BlackWidow X Tournament Edition Chroma, Razer BlackWidow X Ultimate, Razer Blade (Late 2016), Razer Blade (QHD), Razer Blade 14 (2021), Razer Blade 14 (2022), Razer Blade 14 (2023), Razer Blade 14 (2024), Razer Blade 14 (2025), Razer Blade 15 (2018), Razer Blade 15 (2018) Base Model, Razer Blade 15 (2018) Mercury, Razer Blade 15 (2019) Advanced, Razer Blade 15 (2023), Razer Blade 15 (Mid 2019) Base Model, Razer Blade 15 (Mid 2019) Mercury, Razer Blade 15 Advanced (2020), Razer Blade 15 Advanced (Early 2021), Razer Blade 15 Advanced (Early 2022), Razer Blade 15 Advanced (Mid 2021), Razer Blade 15 Studio Edition (2019), Razer Blade 16 (2023), Razer Blade 16 (2025), Razer Blade 17 (2022), Razer Blade 17 Pro (Early 2021), Razer Blade 17 Pro (Mid 2021), Razer Blade 18 (2023), Razer Blade 18 (2024), Razer Blade 18 (2025), Razer Blade Advanced (Late 2019), Razer Blade Base (Early 2020), Razer Blade Base (Early 2021), Razer Blade Base (Early 2022), Razer Blade Late 2020 Base, Razer Blade Pro (2017), Razer Blade Pro (Early 2020), Razer Blade Pro (Late 2016), Razer Blade Pro (Late 2019), Razer Blade Pro 17 (2019), Razer Blade Pro FullHD (2017), Razer Blade Stealth, Razer Blade Stealth (2019), Razer Blade Stealth (Early 2020), Razer Blade Stealth (Late 2016), Razer Blade Stealth (Late 2017), Razer Blade Stealth (Late 2019), Razer Blade Stealth (Late 2020), Razer Blade Stealth (Mid 2017), Razer Book (2020), Razer Charging Pad, Razer Chroma HDK, Razer Chroma Light Strip Set, Razer Chroma Mug Holder, Razer Chroma PC Case Lighting Kit, Razer Cobra, Razer Cobra Pro (Wired), Razer Cobra Pro (Wireless), Razer Core, Razer Core X, Razer Cynosa Chroma, Razer Cynosa Chroma Pro, Razer Cynosa Lite, Razer Cynosa V2, Razer DeathAdder 1800, Razer DeathAdder 2000, Razer DeathAdder 2013, Razer DeathAdder 3.5G, Razer DeathAdder 3500, Razer DeathAdder Chroma, Razer DeathAdder Elite, Razer DeathAdder Essential, Razer Deathadder Essential, Razer DeathAdder Essential (2021), Razer DeathAdder Essential (White Edition), Razer DeathAdder V2, Razer DeathAdder V2 Lite, Razer DeathAdder V2 Mini, Razer DeathAdder V2 Pro (Wired), Razer DeathAdder V2 Pro (Wireless), Razer Deathadder V3, Razer Deathadder V3 Hyperspeed, Razer Deathadder V3 Pro, Razer DeathStalker Chroma, Razer DeathStalker Expert, Razer DeathStalker V2, Razer DeathStalker V2 Pro (Wired), Razer DeathStalker V2 Pro (Wireless), Razer DeathStalker V2 Pro TKL (Wired), Razer DeathStalker V2 Pro TKL (Wireless), Razer DeathStalker/DeathStalker Essential, Razer Diamondback Chroma, Razer Firefly, Razer Firefly Hyperflux, Razer Firefly V2, Razer Firefly V2 Pro, Razer Goliathus, Razer Goliathus Chroma 3XL, Razer Goliathus Extended, Razer Hanbo Cooler, Razer Huntsman, Razer Huntsman Elite, Razer Huntsman Mini, Razer Huntsman Mini Analog, Razer Huntsman Mini JP, Razer Huntsman Tournament Edition, Razer Huntsman V2, Razer Huntsman V2 Analog, Razer Huntsman V2 Tenkeyless, Razer Huntsman V3 HE Magnetic Mini, Razer Huntsman V3 Pro, Razer Huntsman V3 Pro 8KHz, Razer Huntsman V3 Pro Mini, Razer Huntsman V3 Pro TKL, Razer Huntsman V3 X TKL, Razer Imperator 2012, Razer Kraken 7.1 V2 Headset, Razer Kraken Kitty Edition, Razer Kraken Kitty V2, Razer Kraken Ultimate Edition, Razer Kraken V3, Razer Lancehead (Wired), Razer Lancehead (Wireless), Razer Lancehead Tournament Edition, Razer Lancehead Wireless (Receiver), Razer Lancehead Wireless (Wired), Razer Laptop Cooling Pad, Razer Laptop Stand Chroma, Razer Laptop Stand Chroma V2, Razer Leviathan V2, Razer Leviathan V2 X, Razer Mamba 2012 (Wired), Razer Mamba 2012 (Wireless), Razer Mamba Chroma (Wired), Razer Mamba Chroma (Wireless), Razer Mamba Elite, Razer Mamba Hyperflux (Wired), Razer Mamba Tournament Edition, Razer Mamba Wireless (Receiver), Razer Mamba Wireless (Wired), Razer Monitor Stand Chroma, Razer Mouse Bungee V3 Chroma, Razer Mouse Dock Chroma, Razer Mouse Dock Pro, Razer Naga, Razer Naga 2012, Razer Naga Chroma, Razer Naga Classic, Razer Naga Epic, Razer Naga Epic Chroma (Wired), Razer Naga Epic Chroma (Wireless), Razer Naga Hex, Razer Naga Hex (Red), Razer Naga Hex V2, Razer Naga Left Handed Edition 2020, Razer Naga Pro (Wired), Razer Naga Pro (Wireless), Razer Naga Pro V3 (Wired), Razer Naga Pro V3 (Wireless), Razer Naga Trinity, Razer Naga V2 Pro (Wired), Razer Naga V2 Pro (Wireless), Razer Naga X, Razer Nari, Razer Nari Essential, Razer Nari Ultimate Edition, Razer Nommo Chroma, Razer Nommo Pro, Razer Nommo Speakers, Razer Orbweaver, Razer Orbweaver Chroma, Razer Ornata, Razer Ornata Chroma, Razer Ornata V2, Razer Ornata V3, Razer Ornata V3 (Alternate), Razer Ornata V3 Tenkeyless, Razer Ornata V3 X, Razer Ornata V3 X (Alternate), Razer Orochi (Wired), Razer Orochi 2011, Razer Orochi 2013, Razer Orochi V2, Razer Ouroboros, Razer Pro Click V2 (Wired), Razer Pro Click V2 (Wireless), Razer Pro Click V2 Vertical Edition (Wired), Razer Pro Click V2 Vertical Edition (Wireless), Razer Raptor 27 Inch, Razer Raptor 27 Inch Monitor, Razer Seiren Emote, Razer Seiren V3 Mic, Razer Soundbar, Razer Strider Chroma, Razer Taipan, Razer Tartarus, Razer Tartarus Chroma, Razer Tartarus Pro, Razer Tartarus V2, Razer Thunderbolt 4 Dock Chroma, Razer Thunderbolt 5 Dock Chroma, Razer Tiamat 7.1 V2, Razer Turret Keyboard, Razer Turret Mouse, Razer Viper, Razer Viper 8KHz, Razer Viper Mini, Razer Viper Ultimate (Wired), Razer Viper Ultimate (Wireless), Razer Viper V2 Pro, Razer Viper V3 Pro |
| **ASUS** | ASUS Aura Addressable, ASUS Aura Core, ASUS Aura Motherboard, ASUS Cerberus Mech, ASUS laptop keyboard, ASUS Omni keyboard, ASUS PG248QP, ASUS PG27UQ, ASUS PG32UQX, ASUS PG35VQ, ASUS PG43UQ, ASUS ROG Ally, ASUS ROG Ally X, Asus ROG Aura Monitor Light Bar, ASUS ROG AURA Terminal, ASUS ROG Azoth 2.4GHz, ASUS ROG Azoth Extreme, ASUS ROG Azoth Extreme SE, ASUS ROG Azoth USB, ASUS ROG Azoth X, ASUS ROG Balteus, ASUS ROG Balteus Qi, ASUS ROG Bulwark Dock, ASUS ROG Cetra RGB, ASUS ROG Cetra SpeedNova, ASUS ROG Chakram (Wired), ASUS ROG Chakram (Wireless), ASUS ROG Chakram Core, ASUS ROG Chakram X 2.4GHz, ASUS ROG Chakram X USB, ASUS ROG Clavis, ASUS ROG Claymore, ASUS ROG Claymore II, ASUS ROG Delta II, ASUS ROG Delta S, ASUS ROG Falchion (Wired), ASUS ROG Falchion (Wireless), ASUS ROG Falchion Ace, ASUS ROG Falchion Ace HFX, ASUS ROG Falchion RX, ASUS ROG Gladius II, ASUS ROG Gladius II Core, ASUS ROG Gladius II Origin, ASUS ROG Gladius II Origin COD, ASUS ROG Gladius II Origin PNK LTD, ASUS ROG Gladius II Wireless, ASUS ROG Gladius III, ASUS ROG Gladius III Aimpoint, ASUS ROG Gladius III Aimpoint EVA-02, ASUS ROG Gladius III Core, ASUS ROG Gladius III Wireless 2.4Ghz, ASUS ROG Gladius III Wireless AimPoint 2.4Ghz, ASUS ROG Gladius III Wireless AimPoint USB, ASUS ROG Gladius III Wireless Bluetooth, ASUS ROG Gladius III Wireless USB, ASUS ROG Harpe Ace AIM LAB Edition, ASUS ROG Harpe Ace Extreme, ASUS ROG Harpe Ace Mini, ASUS ROG Harpe II Ace, ASUS ROG Harpe Mini Core, ASUS ROG Keris, ASUS ROG Keris II Ace, ASUS ROG Keris II Origin, ASUS ROG Keris II Origin KJP, ASUS ROG Keris Wireless 2.4Ghz, ASUS ROG Keris Wireless AimPoint 2.4Ghz, ASUS ROG Keris Wireless AimPoint USB, ASUS ROG Keris Wireless Bluetooth, ASUS ROG Keris Wireless EVA, ASUS ROG Keris Wireless USB, ASUS ROG Pelta, ASUS ROG PG32UQ, ASUS ROG Pugio, ASUS ROG Pugio II (Wired), ASUS ROG Pugio II (Wireless), ASUS ROG Ryujin AIO, ASUS ROG Ryuo AIO, ASUS ROG Spatha Wired, ASUS ROG Spatha Wireless, Asus ROG Spatha X 2.4GHz, Asus ROG Spatha X USB, ASUS ROG Spotlight, ASUS ROG Strix Claw, ASUS ROG Strix Evolve, ASUS ROG Strix Flare, ASUS ROG Strix Flare CoD Black Ops 4 Edition, ASUS ROG Strix Flare II, ASUS ROG Strix Flare II Animate, ASUS ROG Strix Flare PNK LTD, ASUS ROG Strix Impact, ASUS ROG Strix Impact II, ASUS ROG Strix Impact II Electro Punk, ASUS ROG Strix Impact II Moonlight White, ASUS ROG Strix Impact II Wireless 2.4 Ghz, ASUS ROG Strix Impact II Wireless USB, ASUS ROG Strix Impact III, ASUS ROG Strix LC, ASUS ROG Strix LC III, ASUS ROG Strix SCAR 15, ASUS ROG Strix Scope, ASUS ROG Strix Scope II, ASUS ROG Strix Scope II 96 RX Wireless USB, ASUS ROG Strix Scope II 96 Wireless USB, ASUS ROG Strix Scope II RX, ASUS ROG Strix Scope NX TKL Moonlight White, ASUS ROG Strix Scope NX Wireless Deluxe 2.4GHz, ASUS ROG Strix Scope NX Wireless Deluxe USB, ASUS ROG Strix Scope RX, ASUS ROG Strix Scope RX EVA-02 Edition, ASUS ROG Strix Scope RX TKL Wireless Deluxe, ASUS ROG Strix Scope TKL, ASUS ROG Strix Scope TKL PNK LTD, ASUS ROG Strix XG279Q, Asus ROG STRIX XG27ACDNG, ASUS ROG Strix XG27AQ, Asus ROG STRIX XG27AQDMG, ASUS ROG Strix XG27AQM, Asus ROG STRIX XG27UCG, ASUS ROG Strix XG27W, ASUS ROG Strix XG32VC, Asus ROG SWIFT PG32UCDM, Asus ROG SWIFT PG32UCDMR, Asus ROG SWIFT PG32UCDP, ASUS ROG Throne, ASUS ROG Throne QI, ASUS ROG Throne QI GUNDAM, ASUS Sagaris GK1100, ASUS TUF Gaming K1, ASUS TUF Gaming K3, ASUS TUF Gaming K3 GEN II, ASUS TUF Gaming K3 GEN II Miku, ASUS TUF Gaming K3 GEN II MIKU EDITION, ASUS TUF Gaming K5, ASUS TUF Gaming K7, ASUS TUF Gaming M3, ASUS TUF Gaming M3 Gen II, ASUS TUF Gaming M5, ASUS TUF Gaming Mini Miku, ASUS TX 98 |
| **Corsair** | Corsair Dark Core, Corsair Dark Core Pro SE Wireless, Corsair Dark Core Pro Wireless, Corsair Dark Core RGB Pro SE (Wired), Corsair Dark Core RGB SE (Wired), Corsair Dark Core SE, Corsair Darkstar Wireless, Corsair Glaive RGB, Corsair Glaive RGB PRO, Corsair Harpoon RGB, Corsair Harpoon RGB PRO, Corsair Harpoon Wireless (Wired), Corsair HS80 Max, Corsair HS80 RGB, Corsair HS80 RGB White, Corsair HS80 RGB White Wireless, Corsair HS80 RGB Wired Gaming Headset, Corsair HS80 RGB Wireless, Corsair Ironclaw RGB, Corsair Ironclaw Wireless (Wired), Corsair Ironclaw Wireless SE, Corsair Ironclaw Wireless SE (Wired), Corsair K100 Air, Corsair K100 MX Red, Corsair K100 RGB Optical, Corsair K55 Core, Corsair K55 RGB, Corsair K55 RGB PRO, Corsair K55 RGB PRO XT, Corsair K57, Corsair K57 RGB (Wired), Corsair K60 PRO, Corsair K60 RGB PRO, Corsair K60 RGB PRO Low Profile, Corsair K60 RGB PRO SE, Corsair K60 RGB PRO TKL Black, Corsair K60 RGB PRO TKL White, Corsair K63, Corsair K65 LUX RGB, Corsair K65 Mini, Corsair K65 Plus, Corsair K65 Pro Mini, Corsair K65 RGB, Corsair K65 RGB RAPIDFIRE, Corsair K68 RED, Corsair K68 RED SHADOW, Corsair K68 RGB, Corsair K70 Core, Corsair K70 Core RGB, Corsair K70 Core RGB TKL, Corsair K70 Core TKL Wireless, Corsair K70 LUX, Corsair K70 LUX RGB, Corsair K70 Max, Corsair K70 Pro Mini, Corsair K70 Pro TKL, Corsair K70 RGB, Corsair K70 RGB MK.2, Corsair K70 RGB MK.2 Low Profile, Corsair K70 RGB MK.2 SE, Corsair K70 RGB PRO, Corsair K70 RGB PRO Optomechanical, Corsair K70 RGB PRO V2, Corsair K70 RGB RAPIDFIRE, Corsair K70 RGB TKL, Corsair K70 RGB TKL Champion Series, Corsair K95 RGB, Corsair K95 RGB PLATINUM, Corsair K95 RGB PLATINUM SE, Corsair K95 RGB PLATINUM XT, Corsair Katar, Corsair Katar Pro, Corsair Katar Pro V2, Corsair Katar Pro XT, Corsair Laptop Slipstream Dongle, Corsair Legacy Keyboard, Corsair Legacy Mouse, Corsair M55 RGB PRO, Corsair M65, Corsair M65 PRO, Corsair M65 RGB Elite, Corsair M65 RGB Ultra Wired, Corsair M65 RGB Ultra Wireless (Wired), Corsair M65 Ultra Wireless, Corsair M75, Corsair M75 Gaming Mouse, Corsair M75 Wireless, Corsair M75 Wireless (Wired), Corsair MM700, Corsair MM700 3XL, Corsair MM800 RGB Polaris, Corsair Nexus, Corsair Nightsabre Wireless, Corsair Nightsword, Corsair Sabre Pro, Corsair Sabre Pro Wireless, Corsair Sabre RGB, Corsair Sabre RGB Laser, Corsair Sabre RGB Optical, Corsair Scimitar Elite RGB, Corsair Scimitar Elite Wireless, Corsair Scimitar PRO RGB, Corsair Scimitar RGB, Corsair Slipstream Wireless Receiver HW, Corsair Slipstream Wireless Receiver SW, Corsair ST100 RGB, Corsair Strafe, Corsair Strafe MK.2, Corsair Strafe Red, Corsair Virtuoso, Corsair Virtuoso Max, Corsair Virtuoso SE, Corsair Virtuoso SE Wireless, Corsair Virtuoso Wireless, Corsair Virtuoso XT, Corsair Virtuoso XT Wireless, Corsair Void Elite Headset, Corsair Void Elite Wireless Headset, Corsair Void Pro Headset, Corsair Void Pro USB, Corsair Void Pro Wireless, Corsair Void Wireless V2, Corsair Voyager A1600 |
| **Keychron** | Keychron / Donkey J2 ANSI QMK Keyboard, Keychron C1 Pro QMK Keyboard, Keychron C2 Pro QMK Keyboard, Keychron C3 Pro 8K ANSI QMK Keyboard, Keychron C3 Pro QMK Keyboard, Keychron Gaming Keyboard 1, Keychron K1 Max QMK Keyboard, Keychron K1 Pro QMK Keyboard, Keychron K10 HE ANSI QMK Keyboard, Keychron K10 HE ISO QMK Keyboard, Keychron K10 Max ISO QMK Keyboard, Keychron K10 Max QMK Keyboard, Keychron K10 Pro ISO QMK Keyboard, Keychron K10 Pro QMK Keyboard, Keychron K10 V2 ISO QMK Keyboard, Keychron K10v2 Max QMK Keyboard, Keychron K12 QMK Keyboard, Keychron K17 Max QMK ANSI Keyboard, Keychron K2 HE ANSI QMK Keyboard, Keychron K2 HE ISO QMK Keyboard, Keychron K2 Max ANSI, Keychron K2 Max ISO, Keychron K2 Pro ISO DE QMK Keyboard, Keychron K2 Pro QMK Keyboard, Keychron K2v2+v3 ANSI, Keychron K2v3 ISO, Keychron K3 Pro QMK ISO Keyboard, Keychron K3 Pro QMK Keyboard, Keychron K3v3 ISO, Keychron K4 HE ANSI QMK Keyboard, Keychron K4 Pro, Keychron K4v2 QMK Keyboard, Keychron K5 Max ANSI QMK Keyboard, Keychron K5 Max ISO QMK Keyboard, Keychron K5 Pro QMK Keyboard, Keychron K5 v2 ISO QMK Keyboard, Keychron K6 Pro, Keychron K8 HE ISO QMK Keyboard, Keychron K8 HE QMK Keyboard, Keychron K8 Max ISO QMK Keyboard, Keychron K8 Max QMK Keyboard, Keychron K8 Pro ISO DE QMK Keyboard, Keychron K8 Pro QMK Keyboard, Keychron K8 TKL ISO QMK Keyboard, Keychron K8 v2 ANSI QMK Keyboard, Keychron K8 v2 TKL ISO QMK Keyboard, Keychron Q0 Max QMK Keyboard, Keychron Q0 Plus QMK Keyboard, Keychron Q0 QMK Keyboard, Keychron Q1 HE QMK ANSI Keyboard, Keychron Q1 HE QMK ISO Keyboard, Keychron Q1 Max ANSI QMK Keyboard, Keychron Q1 Max ISO QMK Keyboard, Keychron Q1 Pro / OnePlus 81 Pro QMK Keyboard, Keychron Q1 Pro ISO QMK Keyboard, Keychron Q10, Keychron Q11 QMK Keyboard, Keychron Q12 Max ANSI QMK Keyboard, Keychron Q12 QMK Keyboard, Keychron Q1v1 ISO QMK Keyboard, Keychron Q1v1 QMK Keyboard, Keychron Q1v2 ISO QMK Keyboard, Keychron Q1v2 QMK Keyboard, Keychron Q2 Max ANSI QMK Keyboard, Keychron Q2 Pro ANSI Encoder, Keychron Q2 QMK Keyboard, Keychron Q3 ANSI Encoder Keyboard, Keychron Q3 ANSI Keyboard, Keychron Q3 HE ANSI Encoder Keyboard, Keychron Q3 ISO Keyboard, Keychron Q3 Max ANSI QMK Keyboard, Keychron Q3 Max ISO QMK Keyboard, Keychron Q3 Pro SE ANSI, Keychron Q3 Pro SE ISO QMK Keyboard, Keychron Q4 ANSI, Keychron Q5 HE QMK Keyboard, Keychron Q5 Max ANSI Encoder QMK Keyboard, Keychron Q5 Pro, Keychron Q5 Pro ISO, Keychron Q5 QMK Keyboard, Keychron Q6 HE QMK Keyboard, Keychron Q6 Max ANSI QMK Keyboard, Keychron Q6 Max ISO QMK Keyboard, Keychron Q6 Pro ANSI QMK Keyboard, Keychron Q6 Pro ISO QMK Keyboard, Keychron Q6 QMK Keyboard, Keychron Q65 Max QMK Keyboard, Keychron Q65 QMK Keyboard, Keychron Q8 Max ANSI QMK Keyboard, Keychron Q8 Pro ANSI QMK Keyboard, Keychron V1 ISO QMK Keyboard, Keychron V1 MAX ANSI + Encoder QMK Keyboard, Keychron V1 MAX ISO + Encoder QMK Keyboard, Keychron V1 QMK Keyboard, Keychron V2 QMK Keyboard, Keychron V3 Max QMK ISO Keyboard, Keychron V3 Max QMK Keyboard, Keychron V3 QMK ANSI Keyboard, Keychron V3 QMK ISO Keyboard, Keychron V4 QMK ANSI Keyboard, Keychron V4 QMK ISO Keyboard, Keychron V5 MAX ANSI + Encoder QMK Keyboard, Keychron V5 MAX ISO + Encoder QMK Keyboard, Keychron V5 QMK ANSI Encoder Keyboard, Keychron V5 QMK ISO Encoder Keyboard, Keychron V5 QMK Keyboard, Keychron V6 8K ANSI Encoder QMK Keyboard, Keychron V6 8K ISO Encoder QMK Keyboard, Keychron V6 ANSI QMK Keyboard, Keychron V6 ISO QMK Keyboard, Keychron V6 Max ANSI QMK Keyboard, Keychron V6 Max ISO QMK Keyboard |
| **SteelSeries** | SteelSeries Aerox 3 CS2 Dragon Lore Edition Wireless, SteelSeries Aerox 3 CS2 Dragon Lore Edition Wireless Wired, SteelSeries Aerox 3 Wired, SteelSeries Aerox 3 Wireless, SteelSeries Aerox 3 Wireless Gen 2, SteelSeries Aerox 3 Wireless Wired, SteelSeries Aerox 5 Destiny 2 Edition Wireless, SteelSeries Aerox 5 Destiny 2 Edition Wireless Wired, SteelSeries Aerox 5 Diablo IV Edition, SteelSeries Aerox 5 Diablo IV Edition Wireless, SteelSeries Aerox 5 Diablo IV Edition Wireless Wired, SteelSeries Aerox 5 Wired, SteelSeries Aerox 5 Wireless, SteelSeries Aerox 5 Wireless Wired, SteelSeries Aerox 9 Wireless, SteelSeries Aerox 9 Wireless Wired, SteelSeries Aerox 9 Wireless WOW Edition (2.4 GHz wireless mode), SteelSeries Aerox 9 Wireless WOW Edition (wired mode), SteelSeries Apex (OG)/Apex Fnatic, SteelSeries Apex 3, SteelSeries Apex 3 TKL, SteelSeries Apex 350, SteelSeries Apex 5, SteelSeries Apex 7, SteelSeries Apex 7 TKL, SteelSeries Apex 9 Mini, SteelSeries Apex 9 TKL, SteelSeries Apex M750, SteelSeries Apex M750 TKL, SteelSeries Apex M750 TKL PUBG Edition, SteelSeries Apex Pro, SteelSeries Apex Pro 3, SteelSeries Apex Pro Mini, SteelSeries Apex Pro Mini Gen 3, SteelSeries Apex Pro TKL, SteelSeries Apex Pro TKL 2023 Wired, SteelSeries Apex Pro TKL 2023 Wireless, SteelSeries Apex Pro TKL Gen 3 Wired, SteelSeries Apex Pro TKL Gen 3 Wireless, SteelSeries Arctis 5, SteelSeries Arctis Nova 3, SteelSeries Arctis Pro, SteelSeries Arctis Pro GameDAC, SteelSeries Arena 7, SteelSeries Arena 9, SteelSeries Prime, SteelSeries Prime CS:GO Neo Noir Edition, SteelSeries Prime Mini, SteelSeries Prime Mini Wireless (2.4 GHz wireless mode), SteelSeries Prime Mini Wireless (wired mode), SteelSeries Prime Rainbow 6 Siege Black Ice Edition, SteelSeries Prime Wireless (2.4 GHz wireless mode), SteelSeries Prime Wireless (wired mode), SteelSeries Prime+, SteelSeries QcK Prism, SteelSeries QCK Prism Cloth 3XL, SteelSeries QCK Prism Cloth 4XL, SteelSeries QCK Prism Cloth 5XL, SteelSeries QCK Prism Cloth Medium, SteelSeries QCK Prism Cloth XL, SteelSeries QCK Prism Cloth XL CS:GO Neo Noir Ed., SteelSeries QCK Prism Cloth XL CS:GO Neon Rider Ed., SteelSeries QCK Prism Cloth XL Destiny 2 Lightfall Ed., SteelSeries QCK Prism Cloth XL Destiny Ed., SteelSeries QcK Prism XL Destiny Edition, SteelSeries Rival, SteelSeries Rival 100, SteelSeries Rival 100 (Dell China), SteelSeries Rival 100 DotA 2 Edition, SteelSeries Rival 100 Dota 2 Edition (retail), SteelSeries Rival 105, SteelSeries Rival 106, SteelSeries Rival 110, SteelSeries Rival 3, SteelSeries Rival 3 (Old Firmware), SteelSeries Rival 3 Gen 2, SteelSeries Rival 3 Wireless, SteelSeries Rival 300, SteelSeries Rival 300 CS:GO Fade Edition, SteelSeries Rival 300 CS:GO Fade Edition (stm32), SteelSeries Rival 300 CS:GO Hyperbeast Edition, SteelSeries Rival 300 Dota 2 Edition, SteelSeries Rival 300 Evil Geniuses Edition, SteelSeries Rival 300 Fallout 4 Edition, SteelSeries Rival 300 HP Omen Edition, SteelSeries Rival 300S, SteelSeries Rival 310, SteelSeries Rival 310 CS:GO Howl Edition, SteelSeries Rival 310 PUBG Edition, SteelSeries Rival 5, SteelSeries Rival 5 Destiny Edition, SteelSeries Rival 500, SteelSeries Rival 600, SteelSeries Rival 600 Dota 2 Edition, SteelSeries Rival 650, SteelSeries Rival 650 Wireless, SteelSeries Rival 700, SteelSeries Rival 710, SteelSeries Sensei 310, SteelSeries Sensei [RAW], SteelSeries Sensei TEN, SteelSeries Sensei TEN CS:GO Neon Rider Edition, SteelSeries Siberia 350 |
| **Logitech** | Logitech G13 Keyboard, Logitech G19, Logitech G203 Lightsync, Logitech G203 Prodigy, Logitech G213 Keyboard, Logitech G402 Hyperion Mouse, Logitech G403, Logitech G403 Hero, Logitech G403 Prodigy, Logitech G410 Keyboard, Logitech G413 Keyboard, Logitech G502, Logitech G502 Hero, Logitech G502 Lightspeed, Logitech G502 X, Logitech G502XPlus, Logitech G502XPlusMF, Logitech G512 SE Keyboard, Logitech G513 Keyboard, Logitech G515, Logitech G560 Speakers, Logitech G600 Mouse, Logitech G633, Logitech G635, Logitech G703, Logitech G705, Logitech G713, Logitech G715, Logitech G733, Logitech G735, Logitech G810 Keyboard, Logitech G815 Keyboard, Logitech G9, Logitech G900, Logitech G903, Logitech G910 Keyboard, Logitech G915, Logitech G915 TKL, Logitech G915 X, Logitech G915 X TKL, Logitech G933, Logitech G935, Logitech G9x Original, Logitech GPro 2, Logitech GPro Wired, Logitech GPro Wireless, Logitech GPro X Superlight, Logitech GPro X Superlight 2, Logitech POWERPLAY, Logitech Pro TKL Keyboard, Logitech PRO X 60, Logitech PRO X TKL, Logitech wireless receiver, Logitech X56 HOTAS Joystick, Logitech X56 HOTAS Throttle |
| **Cooler Master** | Cooler Master ARGB, Cooler Master ARGB Gen 2 A1, Cooler Master ARGB Gen 2 A1 Mini, Cooler Master ARGB Gen 2 A1 V2, Cooler Master CK530, Cooler Master CK530 V2, Cooler Master CK550 V1 / CK552, Cooler Master CK550 V2, Cooler Master CK720, Cooler Master CK721, Cooler Master GD160 ARGB Gaming Desk, Cooler Master GM27-FQS ARGB Monitor, Cooler Master GM34-CWQ ARGB Monitor, Cooler Master MasterKeys Pro L, Cooler Master MasterKeys Pro L White, Cooler Master MasterKeys Pro S, Cooler Master MK730, Cooler Master MK750, Cooler Master MK850, Cooler Master MM530, Cooler Master MM711, Cooler Master MM712, Cooler Master MM720, Cooler Master MM730, Cooler Master MP750 Large, Cooler Master MP750 Medium, Cooler Master MP750 XL, Cooler Master MP860 Mouse Pad, Cooler Master Radeon RX 6000 GPU, Cooler Master Radeon RX 6900 GPU, Cooler Master RGB, Cooler Master SK620 Black, Cooler Master SK620 White, Cooler Master SK622 Black, Cooler Master SK622 Keyboard, Cooler Master SK622 White, Cooler Master SK630, Cooler Master SK650, Cooler Master SK650 Keyboard, Cooler Master SK652, Cooler Master SK653, Cooler Master Small ARGB |
| **ROCCAT** | Roccat Burst Core, Roccat Burst Pro, Roccat Burst Pro Air, Roccat Burst Pro Air - Wired, Roccat Elo 7.1, Roccat Elo 7.1 Air, Roccat Horde Aimo, Roccat Kain 100, Roccat Kain 120, Roccat Kain 200, Roccat Kone Aimo, Roccat Kone Aimo 16K, ROCCAT Kone EMP, Roccat Kone Pro, Roccat Kone Pro Air, Roccat Kone Pro Air (Wired), Roccat Kone XP, Roccat Kone XP Air, Roccat Kone XP Air - Wired, Roccat Kone XP Air Dock, Roccat Kova, Roccat Kova Aimo, Roccat Magma, Roccat Magma Mini, Roccat Pyro, Roccat Sense Aimo Mid, Roccat Sense Aimo XXL, Roccat Syn Pro Air, Roccat Torch, Roccat Vulcan 100 Aimo, Roccat Vulcan 120-Series Aimo, Roccat Vulcan II, Roccat Vulcan II Max, Roccat Vulcan II Mini, Roccat Vulcan II Mini Air, Roccat Vulcan Pro, Roccat Vulcan TKL, Roccat Vulcan TKL Pro |
| **HyperX** | HyperX Alloy Elite 2, HyperX Alloy Elite 2 (HP), HyperX Alloy Elite RGB, HyperX Alloy FPS RGB, HyperX Alloy Origins, HyperX Alloy Origins (HP), HyperX Alloy Origins 60, HyperX Alloy Origins 60 (HP), HyperX Alloy Origins 65 (HP), HyperX Alloy Origins Core, HyperX Alloy Origins Core (HP), HyperX DuoCast, HyperX Eve 1800 (HP), HyperX Fury Ultra, HyperX Origins 2 65 (HP), HyperX Pulsefire Core, HyperX Pulsefire Core (HP), HyperX Pulsefire Dart (Wired), HyperX Pulsefire Dart (Wireless), HyperX Pulsefire FPS Pro, HyperX PulseFire FPS Pro, HyperX Pulsefire Haste, HyperX Pulsefire Haste 2, HyperX Pulsefire Haste 2 Mini, HyperX Pulsefire Haste Wireless, HyperX Pulsefire Mat, HyperX Pulsefire Mat RGB Mouse Pad XL, HyperX Pulsefire Raid, HyperX Pulsefire Surge, HyperX Pulsefire Surge (HP), HyperX QuadCast 2 S, HyperX Quadcast S |
| **Cherry** | Cherry Keyboard CCF MX 1.0 TKL BL, Cherry Keyboard CCF MX 1.0 TKL NBL, Cherry Keyboard CCF MX 8.0 TKL BL, Cherry Keyboard G80-3000 TKL NBL, Cherry Keyboard G80-3000 TKL NBL KOREAN, Cherry Keyboard G80-3000 TKL RGB, Cherry Keyboard G80-3000N FL RGB (EU), Cherry Keyboard G80-3000N FL RGB (US), Cherry Keyboard G80-3000N TKL RGB (EU), Cherry Keyboard G80-3000N TKL RGB (US), Cherry Keyboard MV BOARD 3.0 FL RGB, Cherry Keyboard MX 1.0 FL BL, Cherry Keyboard MX 1.0 FL NBL, Cherry Keyboard MX 1.0 FL RGB, Cherry Keyboard MX BOARD 1.0 TKL RGB, Cherry Keyboard MX BOARD 10.0 FL RGB, Cherry Keyboard MX BOARD 10.0N FL RGB (EU), Cherry Keyboard MX BOARD 10.0N FL RGB (US), Cherry Keyboard MX BOARD 2.0S FL NBL, Cherry Keyboard MX BOARD 2.0S FL RGB (EU), Cherry Keyboard MX BOARD 2.0S FL RGB (US), Cherry Keyboard MX BOARD 3.0S FL NBL, Cherry Keyboard MX BOARD 3.0S FL RGB, Cherry Keyboard MX BOARD 3.0S FL RGB KOREAN, Cherry Keyboard MX BOARD 8.0 TKL RGB |
| **Lenovo** | Lenovo 5 2020, Lenovo 5 2021, Lenovo 5 2022, Lenovo 5 2022 Ideapad, Lenovo 5 2023, Lenovo 5 2023 Ideapad, Lenovo Ideapad 3-15ach6, Lenovo Legion 5 Gen 10, Lenovo Legion 7 Gen 10, Lenovo Legion 7 Gen 5, Lenovo Legion 7 Gen 6, Lenovo Legion 7 Gen 7, Lenovo Legion 7 Gen 8, Lenovo Legion 7 Gen 9, Lenovo Legion 7S Gen 5, Lenovo Legion 7S Gen 6, Lenovo Legion 7S Gen 7, Lenovo Legion 7S Gen 8, Lenovo Legion K500, Lenovo Legion K510 Mini Pro, Lenovo Legion M300, Lenovo Legion Y740 |
| **Redragon** | Redragon K667 QMK Keyboard, Redragon M602 Griffin, Redragon M711 Cobra, Redragon M711-FPS-1 Cobra FPS, Redragon M715 Dagger, Redragon M716 Inquisitor, Redragon M801 Sniper, Redragon M808 Storm, Redragon M810 Taipan, Redragon M901-K-2 Perdition, Redragon M901P-KS, Redragon M901P-KS (Wireless), Redragon M908 Impact, Redragon M914 NIX, Redragon M914 NIX (Wireless), Redragon M921 Azzinoth, Redragon M987 Reaping |
| **EVision** | EVision keyboard, EVision Keyboard 0C45:5004, EVision Keyboard 0C45:5104, EVision Keyboard 0C45:5204, EVision Keyboard 0C45:652F, EVision Keyboard 0C45:7672, EVision Keyboard 0C45:7698, EVision Keyboard 0C45:8520, EVision Keyboard 320F:5000, EVision Keyboard 320F:502A, EVision Keyboard 320F:5041, EVision Keyboard 320F:505B, EVision Keyboard 320F:5064, EVision Keyboard 320F:5078, EVision Keyboard 320F:5084 |
| **Alienware** | Alienware 15 R3, Alienware AW2518H, Alienware AW2725DF, Alienware AW3225QF, Alienware AW3418DW, Alienware AW3418HW, Alienware AW3423DW, Alienware AW3423DWF, Alienware AW3821DW, Alienware AW410K, Alienware AW510K, Alienware AW558, Alienware Monitor Gen3 Controller |
| **MSI** | MSI 3-Zone Laptop, MSI Clutch GM11 controller, MSI GE66 Raider, MSI GE68HX Keyboard, MSI GE68HX Lightbar, MSI Keyboard MS 1565, MSI Laptop Keyboard, MSI Laptop Lightbar, MSI Monitor (Gaming Controller), MSI Mystic Light MS 1562, MSI Mystic Light MS 1563, MSI Mystic Light MS 1564, MSI Vigor GK30 controller |
| **Wooting** | Wooting 60HE, Wooting 60HE (ARM), Wooting 60HE+, Wooting 60HEv2, Wooting 80HE, Wooting One, Wooting One (Legacy), Wooting Two, Wooting Two (Legacy), Wooting Two HE, Wooting Two HE (ARM), Wooting Two Lekker Edition, Wooting UwU RGB |
| **Glorious** | Glorious GMMK Pro QMK Keyboard, Glorious Model D / D-, Glorious Model D / D- Wireless, Glorious Model D Wireless, Glorious Model D Wireless - Wired, Glorious Model I, Glorious Model O / O-, Glorious Model O / O- Wireless, Glorious Model O Eternal, Glorious Model O Wireless, Glorious Model O Wireless - Wired |
| **Turtle Beach** | Turtle Beach AIMO Wide Mousepad, Turtle Beach Command Series KP7, Turtle Beach Kone XP Air, Turtle Beach Kone XP Air - Wired, Turtle Beach Kone XP Air Dock, Turtle Beach Vulcan II, Turtle Beach Vulcan II Max Keyboard, Turtle Beach Vulcan II Mini Air, Turtle Beach Vulcan II TKL, Turtle Beach Vulcan II TKL Pro |
| **GaiZhongGai** | GaiZhongGai 17 PRO, GaiZhongGai 17+4+Touch PRO, GaiZhongGai 20 PRO, GaiZhongGai 42 PRO, GaiZhongGai 68+4 PRO, GaiZhongGai Dial, GaiZhongGai LightBoard, GaiZhongGai RGB HUB Blue, GaiZhongGai RGB HUB Green |
| **1upkeyboards** | 1upkeyboards 1upocarina QMK Keyboard, 1upkeyboards 1upsuper16v3 QMK Keyboard, 1upkeyboards pi40 QMK Keyboard, 1upkeyboards pi60 hse QMK Keyboard, 1upkeyboards pi60 QMK Keyboard, 1upkeyboards pi60 rgb QMK Keyboard, 1upkeyboards sweet16v2 QMK Keyboard |
| **EVGA** | EVGA X12 Gaming Mouse, EVGA X15 Mouse, EVGA X17 Mouse, EVGA X20 Gaming Mouse, EVGA X20 USB Receiver, EVGA Z15 Keyboard, EVGA Z20 Keyboard |
| **Lemokey** | Lemokey L1, Lemokey L1 HE, Lemokey L3, Lemokey P1 HE ANSI Keyboard, Lemokey P1 HE ISO Keyboard, Lemokey P1 Pro ANSI Keyboard, Lemokey P1 Pro ISO Keyboard |
| **MonsGeek** | MonsGeek M1 V3, MonsGeek M1 V5 ANSI, MonsGeek M1 V5 ISO, Monsgeek M3 QMK Keyboard, MonsGeek M5 QMK Keyboard, MonsGeek M6 QMK Keyboard, MonsGeek M7 QMK Keyboard |
| **Thermaltake** | ThermalTake Argent E1 Headphone Stand, ThermalTake Argent HS1 Headphone Stand, ThermalTake Argent Mouse Bungee, ThermalTake Argent MP1 Mousepad, Thermaltake Dasher, Thermaltake Level 20 Desk, Thermaltake Poseidon Z RGB |
| **Bloody** | Bloody B820R, Bloody MP 50RS, Bloody W60 Pro, Bloody W70 Max, Bloody W90 Max, Bloody W90 Pro |
| **ZET** | ZET Blade Optical, ZET Fury Pro, ZET GAMING Edge Air Elit, ZET GAMING Edge Air Elit (Wireless), ZET GAMING Edge Air Pro, ZET GAMING Edge Air Pro (Wireless) |
| **Akko** | Akko 3068B Plus / PC75B Plus, Akko 5075 QMK Keyboard, Akko 5108 QMK Keyboard, Akko ACR87 QMK Keyboard, Akko TOP40 QMK Keyboard |
| **Boardsource** | Boardsource Beiwagon QMK Keyboard, Boardsource lulu QMK Keyboard, Boardsource Technik-O QMK Keyboard, Boardsource Technik-S QMK Keyboard, Boardsource The Mark65 QMK Keyboard |
| **Gigabyte** | Gigabyte Aorus 15BKF Backlight, Gigabyte Aorus 15BKF Keyboard, Gigabyte Aorus 17X Backlight, Gigabyte Aorus 17X Keyboard, Gigabyte Aorus M2 |
| **GMMK** | GMMK 2 65% ANSI QMK Keyboard, GMMK 2 65% ISO QMK Keyboard, GMMK 2 96% ANSI QMK Keyboard, GMMK 2 96% ISO QMK Keyboard, GMMK Numpad |
| **NZXT** | NZXT Function, NZXT Function 2, NZXT Function MiniTKL, NZXT Function TKL, NZXT Lift |
| **Drop** | Drop ALT V2 QMK Keyboard, Drop CSTM80 QMK Keyboard, Drop SHIFT v1 QMK Keyboard, Drop SHIFT v2 QMK Keyboard |
| **Fnatic** | Fnatic miniStreak, Fnatic MiniSTREAK Speed, Fnatic Streak, Fnatic Streak65 |
| **Massdrop** | Massdrop ALT, Massdrop CTRL QMK Keyboard, Massdrop CTRL V2 QMK Keyboard, Massdrop SENSE75 QMK Keyboard |
| **Mountain** | Mountain Everest, Mountain Everest 60, Mountain Macropad, Mountain Makalu 67 |
| **NuPhy** | NuPhy Air75 V2 QMK Keyboard, NuPhy Air96 v2 ANSI QMK Keyboard, NuPhy Gem80 QMK Keyboard, NuPhy Halo75 V2 |
| **Sinowealth** | Sinowealth keyboard, Sinowealth Keyboard, Sinowealth mouse 0027, Sinowealth mouse 0051 |
| **YMDK** | YMDK 84, YMDK Idobao x YMDK ID75 QMK Keyboard, YMDK Melody96 RGB QMK Keyboard, YMDK YMD09 QMK Keyboard |
| **Yunzii** | Yunzii AL68, Yunzii AL80 QMK Keyboard, Yunzii MK25047, YUNZII X98 QMK Keyboard |
| **AOC** | AOC AGON AMM700, AOC GK500, AOC GM500 |
| **Controller Works** | Controller Works city42 QMK Keyboard, Controller Works mini36 QMK Keyboard, Controller Works mini42 QMK Keyboard |
| **Das Keyboard** | Das Keyboard 4Q RGB, Das Keyboard 5Q RGB, Das Keyboard 5QS RGB |
| **Epomaker** | Epomaker TH80 Pro (USB Cable), Epomaker TH80 Pro (USB Dongle), Epomaker TH85 QMK Keyboard |
| **KBDfans** | KBDFans KBD67 RGB MKII, KBDfans KBD67MKIIRGB ISO QMK Keyboard, KBDfans KBDPad MKIII QMK Keyboard |
| **Lx3** | Lx3 FAve 84H QMK Keyboard, Lx3 fave60a QMK Keyboard, Lx3 favepada QMK Keyboard |
| **Speedlink** | Speedlink ORIOS RGB Gaming Mouse, Speedlink ORIOS RGB Gaming Mousepad, Speedlink ORIOS RGB Opto-Mech KB |
| **SRGBmods** | SRGBmods LED Controller v1, SRGBmods LED Controller v2, SRGBmods Pico LC |
| **ViewSonic** | ViewSonic Monitor XG270QC, ViewSonic Monitor XG270QG, ViewSonic Monitor XG271QG |
| **Acer** | Acer Nitro keyboard, Acer Predator Gaming Mouse (Rival 300) |
| **Anko** | Anko KM43243952 USB Gaming Mouse, Anko KM43277483 USB Gaming Mouse |
| **Clevo** | Clevo Keyboard (ITE 8291), Clevo Keyboard (ITE 829x) |
| **Cougar** | Cougar 700K EVO Gaming Keyboard, Cougar Revenger ST |
| **Creative** | Creative SoundBlasterX G6, Sound BlasterX Katana |
| **Designed by GG** | Designed by GG Berserker QMK+VIA Keyboard, Designed by GG Ironclad V3 ISO QMK+VIA |
| **Ducky** | Ducky One 2 RGB TKL, Ducky Shine 7/Ducky One 2 RGB |
| **DZTech** | DZTech ANSI DZ60RGB, DZTech DZ65RGB V3 |
| **Framework** | Framework Laptop 16 RGB Keyboard, Framework Laptop 16 RGB Macropad |
| **GameSir** | GameSir Nova 2 Lite, GameSir Nova 2 Lite (Wireless) |
| **Holtek** | Holtek Mousemat, Holtek USB Gaming Mouse |
| **HYTE** | HYTE CNVS, HYTE Keeb TKL |
| **Inland** | Inland KB83 QMK Keyboard, Inland MK47 QMK Keyboard |
| **Ionico** | Ionico Keyboard, Ionico Light Bar |
| **ITE** | ITE 8291 laptop keyboard, ITE 8291 rev 3 laptop keyboard |
| **KBDCraft** | KBDCraft Adam0110 QMK Keyboard, KBDCRAFT Adam64 QMK Keyboard |
| **KBM!** | KBM! TG600 Branco, KBM! TG700 Preto |
| **LG** | LG 27GN950-B Monitor, LG UltraGear 38GL950G |
| **MATTMCCA** | MATTMCCA black hellebore QMK Keyboard, MATTMCCA heliotrope QMK Keyboard |
| **nerdytec** | nerdytec CYKEY QMK ANSI Keyboard, nerdytec CYKEY QMK ISO Keyboard |
| **Patriot** | Patriot Viper V380 Headset, Patriot Viper V550 |
| **Rama Works** | Rama Works M60-B QMK Keyboard, Rama Works M65-B |
| **Red Square** | Red Square Keyrox TKL, Red Square Keyrox TKL V2 |
| **Royal Kludge** | Royal Kludge RK61, Royal Kludge RK84 |
| **Skydimo** | Skydimo Serial, Skydimo SK0902 |
| **Skyloong** | Skyloong GK104 Pro, Skyloong GK68HE Pro |
| **Trust** | Trust GXT 114, Trust GXT 180 |
| **TUXEDO** | TUXEDO Keyboard Light, TUXEDO Light Bar |
| **XBows** | XBows KnightPlus Keyboard, XBows KnightPlus Numpad |
| **A4Tech** | A4Tech Bloody A70x |
| **abko** | abko ak84bt QMK Keyboard |
| **Advanced** | Advanced GTA 250 USB Gaming Mouse |
| **Alpaca Keyboards** | Alpaca Keyboards WhiteFox Eclipse QMK Keyboard |
| **anachronism** | anachronism Tetromino QMK Keyboard |
| **AntEsports** | AntEsports GM600 USB Gaming Mouse |
| **Atlantis** | Atlantis PS17 QMK Keyboard |
| **Attack Shark** | Attack Shark K86 (USB Cable) |
| **B87** | B87 Keyboard |
| **Binepad** | Binepad BN006 QMK Keyboard |
| **BlinkyTape** | BlinkyTape |
| **BY Tech** | BY Tech keyboard |
| **Cerakey** | Cerakey Zen75 QMK ANSI Keyboard |
| **CHOSFOX** | CHOSFOX CHOSFOX CF81 QMK Keyboard |
| **CLEVO** | CLEVO Lightbar |
| **CXT** | CXT cxt studio QMK Keyboard |
| **CZC.Gaming** | CZC.Gaming Dwarf QMK Keyboard |
| **Dark Project** | Dark Project KD3B V2 |
| **dekuNukem** | dekuNukem duckyPad QMK Keyboard |
| **Dell** | Dell G Series LED Controller |
| **depermana12** | depermana12 dp3000 QMK Keyboard |
| **Doio** | Doio doio/kb38 QMK Keyboard |
| **Dream Cheeky** | Dream Cheeky Webmail Notifier |
| **Edifier** | Edifier Halo Pixelbar |
| **eggsworks** | eggsworks egg58 QMK Keyboard |
| **Elgato** | Elgato Stream Deck MK.2 |
| **Endorfy** | Endorfy Omnis |
| **Ergodox** | Ergodox EZ Glow |
| **Everest** | Everest GT-100 RGB |
| **Fancytech** | Fancytech FancyAlice66 QMK Keyboard |
| **Feker** | Feker IK75 (QMK/VIA) |
| **FLASHQUARK** | FLASHQUARK Horizon Z QMK Keyboard |
| **Freja** | Freja 65 Keyboard |
| **Freya** | Freya splaytoraid QMK Keyboard |
| **Genesis** | Genesis Thor 300 |
| **gkeyboard** | gkeyboard GPAD8-2R QMK Keyboard |
| **GMMK3** | GMMK3 QMK Keyboard |
| **Halo96** | Halo96 V2 Keyboard |
| **Hoksi** | Hoksi Technology DURGOD Hades (QMK) QMK Keyboard |
| **IDOBAO** | IDOBAO ID67 |
| **IF99** | IF99 Keyboard |
| **JSAUX** | JSAUX RGB Docking Station |
| **JZ-Skyloong** | JZ-Skyloong DT40 QMK Keyboard |
| **Keebio** | Keebio Nyquistpad QMK Keyboard |
| **KPRepublic** | KPRepublic BM60 Poker Rev 2 |
| **Kuro** | Kuro Kuro65 QMK Keyboard |
| **Laser Ninja** | Laser Ninja Pumpkin Pad QMK Keyboard |
| **Lego** | Lego Dimensions Toypad Base |
| **Lian Li** | Lian Li O11 Dynamic - Razer Edition |
| **LightSalt** | LightSalt Peripherals |
| **Luxafor** | Luxafor Flag |
| **Mad Catz** | Mad Catz Cyborg Gaming Light |
| **Magic Force** | Magic Force / Kinst MF17 QMK Numpad |
| **Mars Gaming** | Mars Gaming MM4 |
| **MCHOSE** | MCHOSE GX87 ANSI QMK Keyboard |
| **Meletrix** | Meletrix Zoom98 QMK Keyboard |
| **N5312A** | N5312A USB Optical Mouse |
| **NCR-80** | NCR-80 Hotswap |
| **Novelkeys** | Novelkeys NK87 QMK Keyboard |
| **Np93** | Np93 ALPHA - Gaming Mouse |
| **Nubwo** | Nubwo X7 Spectrum |
| **Nuvoton** | Nuvoton keyboard |
| **Obinslab** | Anne Pro 2 |
| **OEM** | OEM Wireless Keyboard |
| **OKS** | OKS Optical Axis RGB |
| **Ozone** | Ozone tactical QMK Keyboard |
| **plywrks** | plywrks ply8x QMK Keyboard |
| **ProjectD** | ProjectD ProjectD 65% ANSI QMK Keyboard |
| **Pulsar** | Pulsar XBOARD QS |
| **Rama** | Rama M6-C QMK Keyboard |
| **Raspberry Pi** | Raspberry Pi 500+ |
| **Robobloq** | Robobloq Monitor Light Strip |
| **Royuan** | Royuan keyboard |
| **SayoDevice** | SayoDevice E1 |
| **skeletonkbd** | skeletonkbd Frost68 QMK Keyboard |
| **SKMT** | SKMT SKMT 15k QMK Keyboard |
| **SONIX** | SONIX keyboard |
| **SW** | SW Eave65 |
| **Synth Labs** | Synth Labs 060 QMK Keyboard |
| **System76** | System76 Launch |
| **Tan67** | Tan67 QMK Keyboard |
| **Tecknet** | Tecknet M008 |
| **ThingM** | ThingM blink(1) mk2 |
| **tominabox1** | tominabox1 Le Chiffre QMK Keyboard |
| **Vertagear** | Vertagear RGB LED Upgrade Kits |
| **VSG** | VSG Mintaka |
| **WhirlwindFX** | WhirlwindFX Element V2 ANSI QMK Keyboard |
| **Winbond** | Winbond Gaming Keyboard |
| **Witmod** | Witmod Keyboard |
| **Work Louder** | Work Louder numpad QMK Keyboard |
| **Xiaohua** | Xiaohua keyboard |
| **XPG** | XPG Summoner Gaming Keyboard |
| **Yiancar-Designs** | Yiancar-Designs NK+ QMK Keyboard |
| **zzeneg** | zzeneg stront QMK Keyboard |

---

## Beyond gamepads

PadForge reads these as mapping sources too. Each has its own lane rather than being treated
as a generic joystick.

| Device | What PadForge reads | More |
| --- | --- | --- |
| **DualSense, DualSense Edge** | Gyro, accelerometer, touchpad, adaptive triggers, lightbar, player LEDs, speaker, microphone, mute button, Edge paddles and Fn buttons | [Adaptive Triggers](../features/adaptive-triggers.md) |
| **DualShock 4** | Gyro, accelerometer, touchpad, lightbar, speaker | [Lighting](../features/lighting.md) |
| **DualShock 3** | Motion, pressure-sensitive buttons, pairing over USB | [DualShock 3](dualshock-3.md) |
| **PlayStation Move, Navigation** | Gyro, accelerometer, the lit sphere, analog trigger and d-pad pressure | [PlayStation Move](ps-move.md) |
| **Switch Pro, Switch 2 Pro** | Gyro, accelerometer and rumble. On the original Switch Pro, also the HOME LED and the NFC tag reader | [Lighting](../features/lighting.md), [NFC Tags](../features/nfc-tags.md) |
| **Joy-Con, Joy-Con 2** | Per-half motion, HD Rumble, the right Joy-Con IR camera brightness, the Joy-Con 2 optical mouse, combined-pair motion. Joy-Con 2 clones such as the NYXI Hyperion 3 over Bluetooth: buttons, stick and accelerometer. The report they send leaves out the gyroscope | [Wii Controllers](wii-controllers.md) |
| **Wii Remote, Nunchuk, Classic, Wii U Pro** | Motion, Motion Plus, the IR pointer, the extension port, the speaker | [Wii Controllers](wii-controllers.md) |
| **Wii Balance Board** | Total weight and lean on both axes | [Wii Controllers](wii-controllers.md) |
| **Steam Controller (2015), Steam Controller 2026, Steam Deck** | Trackpads, gyro, haptics, and the 2026 pad's PCM haptic stream. The Steam Deck and the Steam Controller 2026 are also virtual-controller personas, each with its own 2D and 3D body | [Touchpad](../features/touchpad.md), [Virtual Controllers](../features/virtual-controllers.md) |
| **Xbox One, Elite, Series** | Impulse triggers, Guide LED brightness, paddles | [Impulse Triggers](../features/impulse-triggers.md) |
| **Buffalo BSGC101, BSGC201 (Padix PSX/USB converter)** | Rumble on the PS1 or PS2 pad behind the converter, without Buffalo's driver package | [Force Feedback](../features/force-feedback.md#playstation-pads-through-a-padix-converter) |
| **3Dconnexion SpaceMouse** | All six axes of the puck, as ordinary mapping sources | [SpaceMouse](spacemouse.md) |
| **Novint Falcon** | The handle's three axes and the grip's four buttons, with rumble and force feedback played as force on the handle, through Force Dimension's SDK | [Novint Falcon](../features/novint-falcon.md) |
| **Handheld gaming PCs and gaming laptops** | The rear paddles, menu keys and wheels the firmware hides from games, learned by pressing them, plus the machine's own gyroscope and accelerometer | [Handheld PC Buttons](../features/handheld-buttons.md) |
| **VR headsets and controllers** | The headset pose as six axes, and each hand controller's pose, stick, trigger, grip and buttons, through any OpenXR runtime with or without SteamVR. While SteamVR runs, also the headset and every controller it tracks, each as its own device | [VR Controller Input](../features/vr-controller-input.md), [Virtual VR Controllers Internals](../reference/vr-controllers-internals.md#the-other-direction-consuming-real-vr-devices-287) |
| **Sony wireless headsets** | Head rotation as a motion source | [Headset Motion](../features/headset-motion.md) |
| **Head trackers** | A head pose from OpenTrack or anything that speaks its output formats, as six axes | [Head Tracking](../features/head-tracking.md) |
| **MIDI keyboards and pad controllers** | Notes, Control Change, pitch bend and encoders | [MIDI Input](../features/midi-input.md) |
| **NFC readers** | Registered tags as button sources | [NFC Tags](../features/nfc-tags.md) |
| **Keyboards and mice** | Every key, button, wheel and motion axis, per device | [Mappings](../features/mappings.md) |
| **Logitech G-key keyboards and mice** | The G-keys and the extra mouse buttons as their own device row, read through Logitech's G-key SDK | [Logitech G-Keys](../features/logitech-g-keys.md) |
| **Haptic mice: Logitech MX Master 4, SteelSeries Rival 500, 700 and 710** | Rumble from the virtual controller the mouse is assigned to, through its own Force Feedback tab. The MX Master 4 needs no Logitech software, and the Rivals play through SteelSeries GG. Razer Sensa HD hardware takes rumble the same way through the Razer Sensa row | [Force Feedback](../features/force-feedback.md#haptic-mice-and-the-razer-sensa-row) |
| **RGB keyboards, mice, headsets and other lit devices** | Lighting from the virtual controller each is assigned to, turned on from its own Lighting tab: a color or an effect, Screen Color, and per-key colors where the device's lights are known one by one. PadForge lights them over USB itself, [listed above](#rgb-keyboards-mice-and-other-lit-devices). While the maker's program runs, the device is left to it, or lit through it where the program offers an SDK: Razer Synapse, SteelSeries GG, G HUB or Logitech Gaming Software, Armoury Crate's Aura SDK and MSI's Mystic Light SDK. The Razer Chroma, Logitech LIGHTSYNC and SteelSeries GG rows light the headsets, mousepads, speakers and Chroma Link strips PadForge does not read | [Lighting](../features/lighting.md#mice-keyboards-and-vendor-rows), [Mice, Keyboards and Vendor Rows](../features/peripherals.md) |
| **Precision touchpads** | Multi-touch contacts, gestures, per-pad settings | [Touchpad](../features/touchpad.md) |
| **Pens and drawing tablets** | Pen contact as a touchpad finger, plus pressure and pen buttons when the tablet reports them | [Drawing tablets](../features/touchpad.md#drawing-tablets) |
| **Trackballs** | Motion with momentum | [Input Precision](../features/input-precision.md) |
| **Microphones** | Spoken phrases as macro triggers | [Voice Macros](../features/voice-macros.md) |
| **Phones and tablets** | A browser gamepad over Wi-Fi, no app install | [Web Controller](../guides/web-controller.md) |
| **A controller paired to a phone** | Forwarded through the phone's browser: a Bluetooth pad, a telescopic pad clamped around the phone, anything the phone's browser sees as a gamepad. Sticks, triggers, D-pad and up to ten extra buttons on a standard-layout pad, up to 21 buttons and six axes forwarded as reported otherwise, rumble back to the pad where the browser can drive it | [Browser Gamepad](../guides/web-controller.md#browser-gamepad-a-controller-paired-to-the-phone) |
| **Android and Windows gaming handhelds, through their browser** | The handheld's built-in controls forwarded to the PC from the handheld's own browser, the same way. Expected to forward the controls the handheld's browser exposes, within the same limits. Handheld hardware has not been tested here | [Browser Gamepad](../guides/web-controller.md#browser-gamepad-a-controller-paired-to-the-phone) |
| **Another PC's controllers** | Any device above, shared over the network or the internet | [Remote Link](../guides/remote-link.md) |

---

## Virtual keyboards and mice

A Keyboard+Mouse slot can type and point through one of these HIDMaestro models in place of Windows input. Windows and the programs that read devices see the model as that hardware. The tags beside the slot's Keyboard and Mouse pickers show what the model can send, and the mapping table hides the keys, buttons and wheels it cannot. See [Keyboard+Mouse](../features/controller-slots.md#keyboardmouse).

### Keyboards (51)

The preview draws each keyboard as its board's key set. A board drawn as the nearest standard set says so under the picture. **Keys at once** counts the keys besides the modifiers the keyboard can hold down together. A keyboard with a mouse report of its own can also be the slot's mouse, as **Same Device as the Keyboard**.

| Keyboard | Drawn as | Keys at once | Media keys | Lock lights | Mouse report |
| --- | --- | --- | --- | --- | --- |
| 8BitDo Retro Mechanical Keyboard | Tenkeyless | 6 | Yes | Yes |  |
| Apple Keyboard A1243 | Full size, ANSI, nearest set | 5 |  | Yes |  |
| Apple Magic Keyboard A1644 (USB) | 75 percent, nearest set | 6 | Yes | Yes |  |
| Apple Magic Keyboard with Touch ID and Numeric Keypad (USB) | Full size, ANSI, nearest set | 6 | Yes | Yes |  |
| Apple Wireless Keyboard (Bluetooth) | 75 percent, nearest set | 6 |  | Yes |  |
| Cherry G83 (RS 6000) | Full size, ANSI | 6 |  | Yes |  |
| Cherry KC 6000 Slim | Full size, ANSI | 6 |  | Yes |  |
| Cherry Strait 3.0 | Full size, ANSI | 6 |  | Yes |  |
| Cooler Master CK352 | Full size, ANSI | 62 |  | Yes |  |
| Corsair K55 RGB PRO XT | Full size, ANSI | Any | Yes | Yes |  |
| Corsair K70 RGB MK.2 Low Profile | Full size, ANSI | Any | Yes | Yes | 5 buttons, wheel |
| Corsair K70 RGB RAPIDFIRE | Full size, ANSI | 6 |  | Yes |  |
| Corsair K95 RGB Platinum XT | Full size, ANSI | Any | Yes | Yes |  |
| Corsair STRAFE RGB | Full size, ANSI | Any | Yes | Yes |  |
| DREVO BladeMaster TE | Tenkeyless | 61 | Yes | Yes | 5 buttons, wheel |
| Ducky DK2108 | Full size, four keys over the number pad | 6 |  | Yes |  |
| GamaKay LK67 | 65 percent with a blocker | 5 |  | Yes |  |
| Genius Imperator | Full size, ANSI | 6 |  | Yes |  |
| Glorious GMMK Pro | 75 percent | 6 |  | Yes |  |
| HHKB Classic | Happy Hacking | 6 |  | Yes |  |
| HHKB Professional (Topre) | Happy Hacking | 6 |  | Yes |  |
| HHKB Professional JP | Happy Hacking, JIS | 6 |  | Yes |  |
| HHKB Studio (Bluetooth) | Happy Hacking | 6 | Yes | Yes | 5 buttons, wheel, tilt wheel |
| HP USB Keyboard | Full size, ISO | 6 |  | Yes |  |
| HyperX Alloy Elite RGB | Full size, ANSI | 6 |  | Yes |  |
| Keychron Q6 | Keychron Q6 | 6 |  | Yes |  |
| Lenovo ThinkPad Compact Bluetooth Keyboard with TrackPoint | 75 percent, nearest set | 6 | Yes | Yes | 3 buttons, wheel, tilt wheel |
| Lenovo Ultraslim Wireless Combo (keyboard) | Full size, ANSI | 6 |  | Yes |  |
| Logitech Bolt Receiver (keyboard) | Full size, ANSI | Any |  | Yes |  |
| Logitech G710 | Full size, ANSI | 6 |  | Yes |  |
| Logitech G810 | Full size, ANSI | 6 |  | Yes |  |
| Logitech G815 | Full size, ANSI | 6 |  | Yes |  |
| Logitech Unifying Receiver (keyboard) | Full size, ANSI | 6 |  | Yes |  |
| Logitech USB Receiver C52E (keyboard) | Full size, ANSI | 6 |  | Yes |  |
| Microsoft Designer Keyboard (Bluetooth) | 75 percent, nearest set | 10 | Yes | Yes |  |
| Microsoft Natural Ergonomic Keyboard 4000 | Full size, ANSI, nearest set | 6 |  | Yes |  |
| Microsoft Wired Keyboard 600 | Full size, ANSI | 6 |  | Yes |  |
| Obins Anne Pro 2 | 60 percent | 6 |  | Yes |  |
| Raspberry Pi 400 Keyboard | 75 percent, nearest set | 6 |  | Yes |  |
| Razer BlackWidow V3 Mini | 65 percent | 6 |  | Yes |  |
| Razer BlackWidow V4 Pro | Full size, ANSI | 6 |  | Yes |  |
| Razer BlackWidow V4 X | Full size, ANSI | 6 |  | Yes |  |
| Razer Cynosa Chroma Pro | Full size, ANSI | 6 |  | Yes |  |
| Razer DeathStalker V2 Pro | Full size, ANSI | 6 |  | Yes |  |
| Razer Huntsman V3 Pro | Full size, ANSI | 6 |  | Yes |  |
| Razer Ornata V3 | Full size, ANSI | 6 |  | Yes |  |
| Razer Pro Type Ultra | Full size, ANSI | 6 |  | Yes |  |
| Topre Realforce 108 US | Full size, four keys over the number pad | 6 |  | Yes |  |
| Topre Realforce RGB | Full size, ANSI | 6 |  | Yes |  |
| Truly Ergonomic CLEAVE | Tenkeyless, nearest set | 6 |  | Yes |  |
| Varmilo MA109C | Full size, four keys over the number pad | 6 |  | Yes |  |

### Mice (52)

**Buttons** counts the five Windows mouse buttons the model reaches: left, right, middle, back and forward. A mouse with more buttons counts five. A mouse with a keyboard report of its own can also be the slot's keyboard, as **Same Device as the Mouse**.

| Mouse | Buttons | Wheel | Tilt wheel | Keyboard report |
| --- | --- | --- | --- | --- |
| Apple Pro Mouse | 1 |  |  |  |
| ASUS ROG Gladius | 5 | Yes | Yes |  |
| ASUS ROG Spatha | 5 | Yes | Yes |  |
| Corsair Harpoon RGB Wireless | 5 | Yes |  |  |
| Corsair M65 RGB Ultra | 5 | Yes |  |  |
| Corsair Scimitar RGB Elite | 5 | Yes |  | Any keys at once |
| Dell MS116 | 3 | Yes |  |  |
| Genius Gila | 5 | Yes | Yes |  |
| HyperX Pulsefire Dart (cable) | 5 | Yes |  |  |
| HyperX Pulsefire Dart (receiver) | 5 | Yes |  |  |
| Kensington Slimblade Trackball | 2 | Yes |  |  |
| Logitech Bolt Receiver (mouse) | 5 | Yes | Yes |  |
| Logitech G403 HERO | 5 | Yes | Yes |  |
| Logitech G5 | 5 | Yes | Yes |  |
| Logitech G500s | 5 | Yes | Yes |  |
| Logitech G502 HERO | 5 | Yes | Yes |  |
| Logitech G502 X | 5 | Yes | Yes |  |
| Logitech G903 LIGHTSPEED | 5 | Yes | Yes |  |
| Logitech Gaming Mouse G502 | 5 | Yes | Yes |  |
| Logitech M557 (Bluetooth) | 5 | Yes | Yes | 6 keys at once |
| Logitech MX Anywhere 3S (Bluetooth) | 5 | Yes | Yes |  |
| Logitech MX Master 3S (Bluetooth) | 5 | Yes | Yes |  |
| Logitech MX510 | 5 | Yes |  |  |
| Logitech MX518 | 5 | Yes | Yes |  |
| Logitech Unifying Receiver (mouse) | 5 | Yes | Yes |  |
| Logitech USB Optical Mouse | 3 | Yes |  |  |
| Logitech USB Trackball | 5 |  |  |  |
| Microsoft 2.4GHz Transceiver v9.0 (mouse) | 5 | Yes | Yes |  |
| Microsoft Classic IntelliMouse | 5 | Yes |  |  |
| Microsoft Notebook Optical Mouse | 3 | Yes |  |  |
| Microsoft Optical Mouse with Tilt Wheel | 5 | Yes | Yes |  |
| Microsoft Sculpt Touch Mouse (Bluetooth) | 5 | Yes | Yes | 6 keys at once |
| Pulsar Xlite Wireless | 5 | Yes | Yes |  |
| Rapoo M50 Plus Silent | 3 | Yes |  |  |
| Razer Basilisk V2 | 5 | Yes |  |  |
| Razer Basilisk V3 Pro | 5 | Yes | Yes |  |
| Razer Basilisk V3 X HyperSpeed | 5 | Yes | Yes |  |
| Razer Cobra | 5 | Yes |  |  |
| Razer DeathAdder V2 | 5 | Yes |  |  |
| Razer DeathAdder V3 | 5 | Yes |  |  |
| Razer DeathAdder V3 Pro | 5 | Yes |  |  |
| Razer Naga Trinity | 5 | Yes |  |  |
| Razer Orochi V2 | 5 | Yes | Yes |  |
| Razer Viper Mini | 5 | Yes |  |  |
| Razer Viper Ultimate | 5 | Yes |  |  |
| Razer Viper V3 Pro | 5 | Yes |  |  |
| Redragon M690 PRO | 5 | Yes | Yes |  |
| SteelSeries Kana | 5 | Yes |  |  |
| SteelSeries Rival | 5 | Yes |  |  |
| SteelSeries Rival 600 | 5 | Yes | Yes |  |
| Xiaomi Mi Wireless Mouse | 5 | Yes | Yes |  |
| ZOWIE Gaming Mouse | 5 | Yes |  |  |

---

*Last updated for PadForge 5.3.0.*
