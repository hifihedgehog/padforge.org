# Supported Devices

*Every controller, wheel, stick and adapter PadForge knows by name, in one place.*

PadForge recognizes **711** devices by their USB identity: 605 gamepads in SDL's controller list, 3 Flydigi pads its dedicated driver claims, 75 racing wheels, 19 flight sticks, 4 throttles, 32 arcade sticks and 10 GameCube adapters. The arcade sticks, three wheels and two adapters also sit in the gamepad list, so the total is smaller than the sum. Behind those sit **249** shipped gamepad mappings (248 from SDL's Windows database plus PadForge's own DualShock 3 entry) and 231 device profiles.

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
| **PDP** | Afterglow Gamepad 1, Afterglow Gamepad 3, PDP Afterglow AX.1, PDP AFTERGLOW AX.1, PDP Battlefield 4 Controller, PDP EA Soccer Controller, PDP INJUSTICE FightPad, PDP INJUSTICE FightStick, PDP MK X Fight Stick, PDP Versus Fighting Pad, PDP Xbox 360 Afterglow, PDP Xbox 360 Controller, PDP Xbox 360 Marvel Controller, PDP Xbox 360 Rock Candy, Rock Candy Gamepad for Xbox 360 |
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
| **PDP** | Afterglow PS3, afterglow ps3, PDP Afterglow Wireless PS3 controller, PDP Versus Fighting Pad, Rock Candy PS3, Rock Candy PS4 |
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

### PlayStation 4 (63)

| Vendor | Devices |
| --- | --- |
| **NACON** | NACON Asymmetric Controller, NACON Asymmetric Controller Wireless Dongle, NACON Daija Arcade Stick, NACON Daija Fight Stick, Nacon PS4 Compact Controller, NACON PS4 controller in Xbox mode, NACON Revolution 5 Pro, NACON Revolution 5 Pro (PS4 mode wired), NACON Revolution Infinite, Nacon Revolution Pro Controller, NACON Revolution Pro Controller 3, Nacon Revolution Pro Controller v2, NACON Revolution Unlimited, NACON Revolution Unlimited Wireless Dongle, NACON Wireless Controller for PS4 |
| **HORI** | HORI Fighting Commander 4 PS4, HORI Fighting Commander OCTA, HORI Fighting Commander PS4, HORI Fighting Stick mini 4, Hori Fighting Stick mini 4 kai, Hori Fighting Stick α, Hori mini wired, HORI Real Arcade Pro 4, HORI TAC PRO mousething, HORI TAC4 mousething, HORI Wireless Controller Light, HORIPAD 4 FPS, HORIPAD 4 FPS Plus |
| **Razer** | Razer Panthera Evo Fightstick, Razer Raiju 2 Tournament edition BT, Razer Raiju 2 Tournament edition USB, Razer Raiju 2 Ultimate BT, Razer Raiju 2 Ultimate USB, Razer Raiju PS4 Controller, Razer RAION Fightpad |
| **Qanba** | Qanba Dragon, Qanba Dragon Arcade Joystick, Qanba Drone, Qanba Obsidian, Qanba Obsidian Arcade Joystick |
| **Mad Catz** | Mad Catz FightPad Pro PS4, Mad Catz FightStick TE 2 PS4, Mad Catz FightStick TE 2+ PS4, Mad Catz FightStick TE S+ PS4 |
| **PDP** | Victrix Pro FS, Victrix Pro FS PS4/PS5 (PS4 mode), Victrix Pro FS V2 w/ Touchpad for PS4 |
| **Armor** | Armor 3 or Level Up Cobra, Armor Armor 3 Pad PS4 |
| **Sony** | Sony PS4 Controller, Sony PS4 Slim Controller |
| **Astro** | Astro C40 |
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

### Flydigi (3 USB identities)

SDL's Flydigi driver claims these pads by USB identity, then names the model from the controller's own device ID, so one identity covers a family.

| Identity | What the driver claims |
| --- | --- |
| **04B4:2412** | First-generation Flydigi gamepad (vendor protocol on interface 2) |
| **37D7:2501** | Second-generation Flydigi Apex |
| **37D7:2401** | Second-generation Flydigi Vader |

Models the driver names from the device ID: Apex 2, Apex 3, Apex 4, Apex 5, Vader 2, Vader 2 Pro, Vader 3, Vader 3 Pro, Vader 4 Pro and Vader 5 Pro.

The four rear paddles map as Paddle 1 to 4. The Vader series C and Z buttons and the Apex 5 shoulder macro buttons map as Misc 2 and Misc 3, and the Vader 5 Pro's three extra buttons as Misc 4 to 6. The Apex 5, Vader 3 Pro, Vader 4 Pro and Vader 5 Pro report gyro and accelerometer.

### Other (3)

| Vendor | Devices |
| --- | --- |
| **DragonRise** | DragonRise Generic USB PCB, sometimes configured as a PC Twin Shock Controller |
| **Steam** | Steam Virtual Gamepad |
| **Streaming** | Streaming mobile touch virtual controls |

### With a shipped mapping (249)

Pads carrying a mapping in the database, so their buttons and axes land in the right places
the moment they are plugged in. SDL's database holds 248 names in its Windows section, and
PadForge adds one of its own for the DualShock 3 under DsHidMini.

| Vendor | Devices |
| --- | --- |
| **8BitDo** | 8BitDo 64 Bluetooth Controller, 8BitDo FC30 Pro, 8BitDo M30 Gamepad, 8BitDo Micro gamepad, 8BitDo N30 Pro 2, 8BitDo NES30 Gamepad, 8BitDo NES30 Pro, 8BitDo Pro 2, 8BitDo SF30 Pro, 8BitDo SFC30 Gamepad, 8BitDo SN30 Gamepad, 8BitDo SN30 Pro, 8BitDo SN30 Pro+, 8BitDo SNES30 Gamepad, 8BitDo Ultimate 2C Wireless, 8BitDo Ultimate Wired Controller, 8BitDo Ultimate Wireless Controller, 8BitDo Zero 2, 8BitDo Zero Gamepad |
| **HORI** | HORI Fighting Commander, Hori Fighting Commander 4 (PS3), Hori Fighting Commander 4 (PS4), Hori Fighting Stick Mini 3, HORI Fighting Stick mini 4 (PS3), HORI Fighting Stick mini 4 (PS4), Hori Pad 3, Hori Pad 3 Turbo, Hori Pad A, Hori Pokken Tournament DX Pro Pad, Horipad, HORIPAD 4 (PS3), HORIPAD 4 (PS4), HORIPAD mini4, REAL ARCADE PRO.3, Real Arcade Pro.4, REAL ARCADE PRO.4 VLX, REAL ARCADE Pro.V3, Real Arcade Pro.V4 |
| **Mad Catz** | Mad Catz C.T.R.L.R, Mad Catz FightPad PRO (PS3), Mad Catz FightPad PRO (PS4), Mad Catz FightStick TE S+ (PS3), Mad Catz FightStick TE S+ (PS4), Mad Catz FightStick TE2+ PS3, Mad Catz FightStick TE2+ PS4, Mad Catz Micro C.T.R.L.R, Mad Catz TE2 PS3 Fightstick, Mad Catz TE2 PS4 Fightstick, Madcatz Arcade Fightstick TE S PS3, Madcatz Arcade Fightstick TE S+ PS3, MadCatz SFIV FightStick PS3 |
| **Saitek** | Saitek Cyborg, Saitek Cyborg V.1 Game pad, Saitek Dual Analog Pad, Saitek P2500 Force Rumble Pad, Saitek P2900, Saitek P480 Rumble Pad, Saitek P990, Saitek P990 Dual Analog Pad, Saitek PS1000, Saitek PS2700, Saitek Rumble Pad |
| **Logitech** | Logitech ChillStream, Logitech Cordless Precision, Logitech Cordless Wingman, Logitech Dual Action, Logitech F510 Gamepad, Logitech F710 Gamepad, Logitech Precision Gamepad |
| **Qanba** | QanBa Arcade JoyStick 1008, QanBa Arcade JoyStick 4018, Qanba Dragon Arcade Joystick, QanBa Joystick Plus, QanBa Joystick Q4RAF, Qanba Obsidian Arcade Joystick (PS3), Qanba Obsidian Arcade Joystick (PS4) |
| **Razer** | Razer Atrox Arcade Stick, Razer Hydra, Razer Panthera (PS3), Razer Panthera (PS4), Razer Raiju Mobile, Razer Raion Fightpad for PS4, Razer Serval |
| **Mayflash** | Mayflash Arcade Stick, Mayflash N64 Controller Adapter, Mayflash USB Adapter for original Sega Saturn controller, Mayflash Wii Classic Controller, Mayflash WiiU Pro Game Controller Adapter (DInput) |
| **Thrustmaster** | Thrustmaster Dual Analog 4, Thrustmaster Dual Trigger 3-in-1, ThrustMaster eSwap PRO Controller, Thrustmaster Firestorm Dual Power, Thrustmaster Firestorm Dual Power 3 |
| **Betop** | Betop 2126F, Betop BFM Gamepad, Betop Controller, Betop Gamepad |
| **Genius** | Genius, Genius Maxfire Blaze 3, Genius Maxfire Grandias 12, Genius MaxFire Grandias 12V |
| **PDP** | Afterglow PS3 Controller, PDP Versus Fighting Pad, Rock Candy PS3 Controller, Victrix Pro Fight Stick for PS4 |
| **PowerA** | PowerA OPS v1 Wireless Controller, PowerA OPS v3 Pro Wireless Controller, PowerA Pro Ex, PowerA Wired GameCube Controller |
| **Gioteck** | Gioteck, Gioteck PS3 Controller, Gioteck VX2 Controller |
| **ROG** | ROG Chakram, ROG Chakram Core, ROG Chakram X |
| **SteelSeries** | SteelSeries, SteelSeries Stratus Duo, SteelSeries Stratus XL |
| **USB** | USB 4-Axis 12-Button Gamepad, USB Gamepad, USB Vibration Joystick (BM) |
| **Defender** | Defender Game Racer X7, Defender Joystick Cobra R4 |
| **Dual** | Dual Box WII, Dual USB Vibration Joystick |
| **EXEQ** | EXEQ, EXEQ RF USB Gamepad 8206 |
| **Game** | Game Controller for PC, Game VIB Joystick |
| **GameSir** | GameSir, GameSir T4 Pro |
| **GameStop** | GameStop Gamepad, GameStop PS4 Fun Controller |
| **iBUFFALO** | iBUFFALO BSGP1204 Series, iBUFFALO BSGP1204P Series |
| **MOGA** | MOGA XP5-A Plus, MOGA XP5-X Plus |
| **Nintendo** | Nintendo GameCube Controller, Nintendo Retrolink USB Super SNES Classic Controller |
| **Pro** | Pro Elite PS3 Controller, Pro Ex mini PS3 Controller |
| **PS** | PS Controller, PS to USB convert cable |
| **PS3** | PS3 Controller, PS3 RF pad |
| **RetroUSB.com** | RetroUSB.com RetroPad, RetroUSB.com Super RetroPort |
| **Revolution** | Revolution Pro Controller, Revolution Pro Controller 3 |
| **3DRUDDER** | 3DRUDDER |
| **Acme** | Acme GA-02 |
| **Acteck** | Acteck AGJ-3200 |
| **Airflo** | Airflo PS3 Controller |
| **Amazon** | Amazon Luna Controller |
| **ASUS** | ASUS ROG Kunai 3 Gamepad |
| **Batarang** | Batarang |
| **Battalife** | Battalife Joystick |
| **Battlefield** | Battlefield 4 PS3 Controller |
| **BDA** | BDA PS4 Fightpad |
| **Bigben** | Bigben PS3 Controller |
| **BrutalLegendTest** | BrutalLegendTest |
| **BUFFALO** | BUFFALO BSGP1601 Series |
| **Cideko** | Cideko AK08b |
| **Cyber** | Cyber Gadget GameCube Controller |
| **Cyborg** | Cyborg V.3 Rumble Pad |
| **EA** | EA SPORTS PS3 Controller |
| **Elecom** | Elecom Gamepad |
| **FF-GP1** | FF-GP1 |
| **FIGHTING** | FIGHTING STICK V3 |
| **Gamecube** | Gamecube Controller |
| **Gamepad** | Gamepad Pro USB |
| **GAMEPAD** | GAMEPAD 3 TURBO |
| **GameSir-T3** | GameSir-T3 2.02 |
| **GGE909** | GGE909 Recoil Pad |
| **Google** | Google Stadia Controller |
| **Hama** | Hama Scorpad |
| **Hatsune** | Hatsune Miku Sho Controller |
| **HitBox** | HitBox Edition Cthulhu+ |
| **HJD-X** | HJD-X |
| **HRAP2** | HRAP2 on PS/SS/N64 Joypad to USB BOX |
| **HuiJia** | HuiJia SNES Controller |
| **iBuffalo** | iBuffalo SNES Controller |
| **Impact** | Impact Black |
| **INJUSTICE** | INJUSTICE FightStick PS3 Controller |
| **IPEGA** | IPEGA |
| **Ipega** | Ipega PG-9023 |
| **JC-P301U** | JC-P301U |
| **JC-U3613M** | JC-U3613M (DInput) |
| **JC-W01U** | JC-W01U |
| **King** | King PS3 Controller |
| **MADCATZ** | MADCATZ SFV Arcade FightStick Alpha PS4 |
| **Matricom** | Matricom |
| **MLG** | MLG Gamepad PS3 Controller |
| **Monect** | Monect Virtual Controller |
| **MP-8866** | MP-8866 Super Dual Box |
| **NACON** | NACON GC-400ES |
| **NEXT** | NEXT SNES Controller |
| **NGDS** | NGDS |
| **Nintendo Switch** | Nintendo Switch Pro Controller |
| **Nostromo** | Nostromo N45 |
| **NVIDIA** | NVIDIA Virtual Gamepad |
| **NYKO** | NYKO AIRFLO EX |
| **Oklick** | Oklick W-2 |
| **Onlive** | Onlive Wireless Controller |
| **OPP** | OPP PS3 Controller |
| **Orange** | Orange Controller |
| **OrangeFox86** | OrangeFox86 DreamPicoPort |
| **OUYA** | OUYA Game Controller |
| **P4** | P4 Wired Gamepad |
| **Piranha** | Piranha xtreme |
| **PS1** | PS1 Controller |
| **PS2** | PS2 Controller |
| **PS360+** | PS360+ v1.66 |
| **PS4** | PS4 Controller |
| **PS5** | PS5 Controller |
| **QANBA** | QANBA DRONE ARCADE JOYSTICK |
| **Retro** | Retro Fighters D6 |
| **Retrolink** | Retrolink SNES Controller |
| **run'n'drive** | run'n'drive |
| **RX** | RX Gamepad |
| **Saturn_Adapter_2.0** | Saturn_Adapter_2.0 |
| **SL-6555-SBK** | SL-6555-SBK |
| **SL-6566** | SL-6566 |
| **Sony** | Sony DualShock 3 (DsHidMini SDF and SXS) |
| **Speedlink** | Speedlink Torid |
| **SpeedLink** | SpeedLink Strike FX |
| **SPEEDLINK** | SPEEDLINK STRIKE Gamepad |
| **SplitFish** | SplitFish Game Controller |
| **Steam** | Steam Virtual Gamepad |
| **STK-7024X** | STK-7024X |
| **SVEN** | SVEN X-PAD |
| **SZMY-POWER** | SZMY-POWER PC Gamepad |
| **T** | T Mini Wireless |
| **Team** | Team 5 |
| **Techmobility** | Techmobility X6-38V |
| **TigerGame** | TigerGame PS/PS2 Game Controller Adapter |
| **Tournament** | Tournament PS3 Controller |
| **Trust** | Trust Gamepad |
| **TwinShock** | TwinShock PS2 |
| **uRage** | uRage Gamepad |
| **Venom** | Venom Arcade Joystick |
| **Void** | Void Gaming Void GENESIS |
| **Xeox** | Xeox |
| **XEOX** | XEOX Gamepad SL-6556-BK |
| **XiaoMi** | XiaoMi Game Controller |
| **Xin-Mo** | Xin-Mo Dual Arcade |
| **ZD-T** | ZD-T Android |
| **ZENAIM** | ZENAIM ARCADE CONTROLLER |
| **ZEROPLUS** | ZEROPLUS P4 Wired Gamepad |

---

## Racing wheels (58)

**Driven in the wheel's own protocol**, with rotation range, autocenter and the LED strip on
the wheels that have them: the Logitech, Thrustmaster and Fanatec models. Everything else is
recognized as a wheel and takes force feedback through the standard path. See
[Force Feedback](../features/force-feedback.md).

| Vendor | Devices |
| --- | --- |
| **Logitech** | Logitech Driving Force GT, Logitech Driving Force Pro, Logitech G25, Logitech G27, Logitech G29, Logitech G920, Logitech G923, Logitech G923 for Playstation 4 and PC, Logitech generic wheel, Logitech Momo Force, Logitech Momo Racing, Logitech PRO Racing Wheel, Logitech PRO Racing Wheel for Xbox |
| **Fanatec** | Fanatec ClubSport Wheel Base V1, Fanatec ClubSport Wheel Base V2, Fanatec ClubSport Wheel Base V2.5, Fanatec CSL Elite, Fanatec CSL Elite Wheel Base+, Fanatec Forza Motorsport, Fanatec generic wheel / CSL DD / GT DD Pro, Fanatec Podium Wheel Base DD1, Fanatec Podium Wheel Base DD2, Fanatec Porsche Wheel |
| **Thrustmaster** | Thrustmaster T150, Thrustmaster T248, Thrustmaster T300RS, Thrustmaster T500RS, Thrustmaster TMX, Thrustmaster TS-XW, Thrustmaster TX, Thrustmaster Wheel FFB |
| **Padix** | Padix Force Feedback Wheel, Padix TW6 Wheel, Padix USB Wheel, Padix USB Wireless 2.4GHz Wheel, Padix USB Wireless 2.4GHz Wheelpad, Padix Vibration USB Wheel |
| **MOZA** | Moza R12, Moza R16/R21, Moza R3, Moza R5, Moza R9 |
| **Asetek SimSports** | Asetek SimSports Forte, Asetek SimSports Invicta, Asetek SimSports La Prima, Asetek SimSports Tony Kannan |
| **Simucube** | Simucube 1, Simucube 2 Pro, Simucube 2 Sport, Simucube 2 Ultimate |
| **Cammus** | Cammus C12, Cammus C5 |
| **DragonRise** | DragonRise Wired Wheel |
| **Generic** | Generic FFBoard OpenFFBoard universal forcefeedback wheel |
| **PXN** | PXN VD6 |
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

### Sticks (18)

| Vendor | Devices |
| --- | --- |
| **Padix** | Padix MetalStrike ForceFeedback, Padix MetalStrike Pro, Padix QF-688uv Windstorm Pro, Padix QF-707u Bazooka, Padix USB joystick with viewfinder, Padix USB vibration joystick with viewfinder, Padix USB Wireless 2.4GHZ, Padix USB Wireless 2.4GHz, Padix Wireless MetalStrike |
| **Thrustmaster** | HOTAS Warthog Joystick, ThrustMaster T.16000M Joystick |
| **VIRPIL Controls** | VIRPIL Controls L-VPC Stick MT-50CM3, VIRPIL Controls R-VPC Stick MT-50CM3 |
| **Logitech** | Logitech Extreme 3D |
| **Saitek** | Saitek Pro Flight X-56 Rhino Stick |
| **Turtle Beach** | Turtle Beach VelocityOne |
| **VKB** | Gunfighter Mk.III 'Space Combat Edition' |
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
| **HORI** | Hori Fighting Stick Alpha in PC Mode, Hori Fighting Stick Alpha in PS4 Mode, Hori Fighting Stick Alpha in PS5 Mode, Hori Fighting Stick mini 4 kai, HORI Real Arcade Pro 4, Hori Real Arcade Pro 4, Hori Real Arcade Pro Hayabusa Xbox One, HORI Real Arcade Pro V Hayabusa in Switch Mode, Hori Real Arcade Pro V Kai 360, Hori Real Arcade Pro V Kai Xbox One, Hori Real Arcade Pro VX, Hori Real Arcade Pro VX-SA, Hori Real Arcade Pro. EX, Hori Real Arcade Pro.EX, Hori Real Arcade Pro.EX Premium VLX, Hori Real Arcade Pro.VX SA, Real Arcade Pro 4 |
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
| **GameCube** | GameCube {HuiJia USB box} |
| **Nintendo** | Nintendo Wii U GameCube Controller Adapter |
| **Nintendo Switch** | Nintendo Switch 2 NSO GameCube Controller |
| **PDP** | PDP Wired Fight Pad Pro for Nintendo Switch |
| **PowerA** | PowerA Wired Controller Nintendo GameCube Style |

---

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

## Beyond gamepads

PadForge reads these as mapping sources too. Each has its own lane rather than being treated
as a generic joystick.

| Device | What PadForge reads | More |
| --- | --- | --- |
| **DualSense, DualSense Edge** | Gyro, accelerometer, touchpad, adaptive triggers, lightbar, player LEDs, speaker, microphone, mute button, Edge paddles and Fn buttons | [Adaptive Triggers](../features/adaptive-triggers.md) |
| **DualShock 4** | Gyro, accelerometer, touchpad, lightbar, speaker | [Lighting](../features/lighting.md) |
| **DualShock 3** | Motion, pressure-sensitive buttons, pairing over USB | [DualShock 3](dualshock-3.md) |
| **PlayStation Move, Navigation** | Gyro, accelerometer, the lit sphere, analog trigger and d-pad pressure | [PlayStation Move](ps-move.md) |
| **Switch Pro, Switch 2 Pro** | Gyro, accelerometer, HOME LED, rumble, NFC on the pads that have it | [Wii Controllers](wii-controllers.md) |
| **Joy-Con, Joy-Con 2** | Per-half motion, HD Rumble, the right Joy-Con IR camera brightness, the Joy-Con 2 optical mouse, combined-pair motion | [Wii Controllers](wii-controllers.md) |
| **Wii Remote, Nunchuk, Classic, Wii U Pro** | Motion, Motion Plus, the IR pointer, the extension port, the speaker | [Wii Controllers](wii-controllers.md) |
| **Wii Balance Board** | Total weight and lean on both axes | [Wii Controllers](wii-controllers.md) |
| **Steam Controller (2015), Steam Controller 2026, Steam Deck** | Trackpads, gyro, haptics, and the 2026 pad's PCM haptic stream. The Steam Deck and the Steam Controller 2026 are also virtual-controller personas, each with its own 2D and 3D body | [Touchpad](../features/touchpad.md), [Virtual Controllers](../features/virtual-controllers.md) |
| **Xbox One, Elite, Series** | Impulse triggers, Guide LED brightness, paddles | [Impulse Triggers](../features/impulse-triggers.md) |
| **3Dconnexion SpaceMouse** | All six axes of the puck, as ordinary mapping sources | [SpaceMouse](spacemouse.md) |
| **Handheld gaming PCs and gaming laptops** | The rear paddles, menu keys and wheels the firmware hides from games, learned by pressing them, plus the machine's own gyroscope and accelerometer | [Handheld PC Buttons](../features/handheld-buttons.md) |
| **VR controllers** | Any OpenVR controller through SteamVR, as a slot with hand roles | [VR Controllers](../features/vr-controllers.md) |
| **Sony wireless headsets** | Head rotation as a motion source | [Headset Motion](../features/headset-motion.md) |
| **MIDI keyboards and pad controllers** | Notes, Control Change, pitch bend and encoders | [MIDI Input](../features/midi-input.md) |
| **NFC readers** | Registered tags as button sources | [NFC Tags](../features/nfc-tags.md) |
| **Keyboards and mice** | Every key, button, wheel and motion axis, per device | [Mappings](../features/mappings.md) |
| **Precision touchpads** | Multi-touch contacts, gestures, per-pad settings | [Touchpad](../features/touchpad.md) |
| **Trackballs** | Motion with momentum | [Input Precision](../features/input-precision.md) |
| **Microphones** | Spoken phrases as macro triggers | [Voice Macros](../features/voice-macros.md) |
| **Phones and tablets** | A browser gamepad over Wi-Fi, no app install | [Web Controller](../guides/web-controller.md) |
| **A controller paired to a phone** | Forwarded through the phone's browser: a Bluetooth pad, a telescopic pad clamped around the phone, anything the phone's browser sees as a gamepad. Sticks, triggers, D-pad and up to ten extra buttons on a standard-layout pad, up to 21 buttons and six axes forwarded as reported otherwise, rumble back to the pad where the browser can drive it | [Browser Gamepad](../guides/web-controller.md#browser-gamepad-a-controller-paired-to-the-phone) |
| **Android and Windows gaming handhelds, through their browser** | The handheld's built-in controls forwarded to the PC from the handheld's own browser, the same way. Expected to forward the controls the handheld's browser exposes, within the same limits. Handheld hardware has not been tested here | [Browser Gamepad](../guides/web-controller.md#browser-gamepad-a-controller-paired-to-the-phone) |
| **Another PC's controllers** | Any device above, shared over the network or the internet | [Remote Link](../guides/remote-link.md) |

---

*Last updated for PadForge 4.5.0.*
