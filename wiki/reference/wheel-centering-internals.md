# Wheel Centering Internals

*How Vehicle mode turns a car, a speed and a grip into a centering force: the steering model and its sources, the cars, the split between the wheel's firmware and the PC, the stability rule, the oscillation guard, and the Release Test.*

This is the developer-side companion to [Wheel Centering](../features/wheel-centering.md). The vendor writers it rides on are on [Wheel Force Feedback Internals](wheel-ffb-internals.md).

No wheel has run this code. Every stability figure and every Release Test result below comes from `WheelPlant`, a simulated wheel, and from the engine tests (`WheelCenteringTests`, `ReleaseTestTests`, `SteeringModelTests`). The wire side rests on new-lg4ff, hid-fanatecff and hid-tmff2, read as documentation.

---

## Files

| File | Role |
|---|---|
| `PadForge.Engine/Common/Steering/SteeringModel.cs` | The tire and steering model, `SteeringCurve` (the torque table one wheel steps through) and `SteeringMeasures` (the four measures on the card). |
| `PadForge.Engine/Common/Steering/SteeringVehicle.cs` | `SteeringFeel` and the five cars. |
| `PadForge.Engine/Common/Steering/RoadGrip.cs` | Grip figures by surface. |
| `PadForge.Engine/Common/Steering/SpeedUnits.cs` | Miles or kilometers by Windows region, and the starting fixed speed. |
| `PadForge.Engine/Common/Steering/WheelTorqueList.cs` | The makers' torque figures. |
| `PadForge.Engine/Common/Steering/WheelCentering.cs` | `CenteringSettings`, `CenteringFrame` and the composer, `WheelCentering`. |
| `PadForge.Engine/Common/Steering/OscillationGuard.cs` | Watches for a wheel that swings by itself. |
| `PadForge.Engine/Common/Steering/WheelCalibration.cs` | What the Release Test measured, and its saved form. |
| `PadForge.Engine/Common/Steering/ReleaseTest.cs` | The Release Test, one step per poll. |
| `PadForge.Engine/Common/Steering/WheelPlant.cs` | The simulated wheel the test's damping search and the tests run on. |
| `PadForge.Engine/Common/Steering/WheelCenteringRuntime.cs` | One wheel's composer, measurement and test, behind one lock, for the polling thread and the UI. |
| `PadForge.App/Common/Input/WheelCenteringFacts.cs` | What a device's wheel can do, which decides the card. |
| `PadForge.App/Common/Input/WheelCenteringWriter.cs` | Sends a frame to a Logitech, Fanatec or Thrustmaster wheel. |
| `PadForge.App/Common/Input/InputManager.Step2.UpdateInputStates.cs` | `StepWheelCentering` and the vendor block of `ApplyForceFeedback`. |
| `PadForge.Engine/Common/ForceFeedbackState.cs` | `ApplyCentering`, the path for a wheel routed through SDL. |
| `PadForge.App/ViewModels/PadViewModel.Centering.cs` | The card's settings, preview and live readouts. |
| `PadForge.App/Views/ReleaseTestDialog.xaml` and `.xaml.cs` | The Release Test window. |
| `PadForge.App/Controls/SteeringCharts.cs` | `SteeringTorqueChart` and `ReleaseTraceChart`. |

---

## The model

The model is Balachandran and Gerdes, "Designing Steering Feel for Steer-by-Wire Vehicles Using Objective Measures," IEEE/ASME Transactions on Mechatronics ([doi:10.1109/TMECH.2014.2324593](https://doi.org/10.1109/TMECH.2014.2324593)), taken at steady cornering. For a handwheel angle, a speed and a grip it gives the torque the steering puts on the rim. The paper's damping and inertia terms are zero when nothing moves, and the wheel renders damping itself.

- **Car.** The paper's bicycle model (its equations 14 to 17) with nothing changing. Front and rear lateral force carry the lateral acceleration through each axle's share of the mass, and the road wheel angle that holds a lateral acceleration is L a<sub>y</sub> / U² + α<sub>f</sub> − α<sub>r</sub> (`RoadWheelAngle`).
- **Tire.** The Fiala brush model (equation 8). With x = C tan(α) / (3 μ F<sub>z</sub>), the force is μ F<sub>z</sub> (1 − (1 − x)³) up to x = 1 and μ F<sub>z</sub> past it (`FialaForce`, `FialaSlip`).
- **Torque.** The tire moment gain times the power assist weighting times the aligning moment plus the jacking torque (equations 4, 7 and 9 to 13, `TorqueAt`). The aligning moment is the front lateral force times the mechanical trail plus the pneumatic trail. The pneumatic trail falls in a line with tan(α) and is gone where the tire slides. The jacking torque is a spring in road wheel angle with no dead band. The assist weighting is a Gaussian in front slip angle above a lower limit.

Every car uses a 20 mm mechanical trail and a 30 mm pneumatic trail at zero slip. No source below prints a trail. The brush model puts the pneumatic trail at a third of half the contact length (Pacejka, *Tire and Vehicle Dynamics*), which is 30 mm for a 180 mm contact patch.

`SteeringCurve` samples the curve once into 513 points from center to lock, spaced as the square of the step so they crowd near center, where the curve is steep. Below 0.5 m/s it runs at 0.5 m/s, since the bicycle model divides by the speed squared. Past the last steady state the car turns no harder, and the extra angle is front slip. The composer rebuilds the curve in place as the speed moves in quarter meters a second and the grip in fiftieths, and holds a step until the reading is three quarters of a step away, so a speed that wavers between two steps keeps one curve. A moving car costs the polling thread work but no allocation.

`SteeringFeel` holds the four settings the paper's Table II ties to the measures: the tire moment gain (torque stiffness), the jacking stiffness (on-center feel), and the assist weighting's width and lower limit (linearity). Steering Weight scales the gain, On-Center Feel the jacking stiffness, and Power Assist how far the weighting falls below 1, down to a floor of 0.05 so the torque never falls to nothing (`SteeringFeel.Scaled`).

The four measures on the card come from the weave test of ISO 13674-1, as the paper states them, read off the steady curve by least squares over samples a fiftieth of a degree apart (`SteeringMeasures.From`). On-center feel is the torque gradient up to 0.05 g. Torque stiffness is the gradient over the first fifth of the angle that gives 0.2 g. Linearity is the gradient between 0.10 and 0.15 g over the on-center feel.

---

## The cars

| Car | Source | Mass, a, b | Stated by PadForge |
|---|---|---|---|
| Sedan (the default) | BMW 320i, `parameters_vehicle2.yaml` of commonroad-vehicle-models 3.0.2 (Althoff and Würsching, "CommonRoad: Vehicle Models," 2020) | 1093.3 kg, 1.156 m, 1.423 m | Ratio 16, steering sensitivity 1.00 g per 100°, on-center feel 17 N·m/g and linearity 25% at 60 mph, which is what the paper chose for its own car |
| Compact | Ford Escort, `parameters_vehicle1.yaml` of the same source, from the U.S. DOT vehicle dynamics data | 1225.9 kg, 0.884 m, 1.509 m | Ratio 17, sensitivity 1.10, on-center feel 14 N·m/g, linearity 30% |
| Van | VW Vanagon, `parameters_vehicle3.yaml` of the same source | 1478.9 kg, 1.151 m, 1.321 m | Ratio 19, sensitivity 0.70, on-center feel 12 N·m/g, linearity 20% |
| Race Car | The car of TUM's race trajectory planner, `params/racecar.ini` of TUMFTM/global_racetrajectory_optimization at a9995e2 | 1200 kg, 1.6 m, 1.4 m | Ratio 12, on-center feel 26 N·m/g, linearity 80% (little assist). Its sensitivity, 3.6 g per 100° at 60 mph, is far above a production car's. |
| Stanford X1 | The paper's own test car, its Table I | 1973 kg, 1.53 m, 1.23 m, cornering stiffness 110 and 148 kN/rad | Ratio 16 (the paper prints none). The feel is fitted to the paper's Table III. |

For the three CommonRoad cars, an axle's cornering stiffness is 21.92 times its load, from the tire's p_ky1 of −21.92 in `parameters_tire.yaml`: the single-track model takes lateral force as μ C<sub>S</sub> F<sub>z</sub> α with μ = p_dy1 and C<sub>S</sub> = −p_ky1 / p_dy1 (`vehicle_dynamics_st.py`, lines 41 to 43), and the two multiply to 21.92. The rear axle takes that stiffness. The front axle takes a lower effective stiffness, as steering compliance gives a real car: the one that puts the linear model's steering sensitivity at 60 mph on the figure stated for the car (`SteeringVehicle.Production`). Each stated sensitivity sits inside the 0.27 to 1.42 range the paper's Table III gives for production cars.

The race car's tires are Magic Formula tires with B 10, C 2.5 and D = F<sub>z</sub> (1 − 0.1 F<sub>z</sub> / 3000) at a friction coefficient of 1. A tire's cornering stiffness is B C D at its static load, and an axle has two.

With ratio 16 the Stanford X1's steering sensitivity is 2.48 and 0.49 g per 100° at 60 and 25 mph, where the paper's Table III gives 2.33 and 0.52. Its feel is fitted to the paper's on-center feel, 17 and 22 N·m/g at 60 and 25 mph, and to a linearity of 25% at 60 mph.

---

## Grip

The figures are the peak coefficients of road adhesion in J. Y. Wong, *Theory of Ground Vehicles*, 2nd ed. (1993), p. 26, each taken over dry asphalt's 0.85, the middle of its 0.80 to 0.90 range, and kept to two places (`RoadGrip`).

| Surface | Wong's figure | Grip |
|---|---|---|
| Dry asphalt | 0.80–0.90 | 1.00 |
| Wet asphalt | 0.50–0.70 | 0.71 |
| Gravel | 0.60 | 0.71 |
| Dry earth road | 0.68 | 0.80 |
| Wet earth road | 0.55 | 0.65 |
| Hard-packed snow | 0.20 | 0.24 |
| Ice | 0.10 | 0.12 |

Grass and sand are not in Wong's table and read as the wet earth road. A wetness from 0 to 1 runs between dry and wet asphalt (`RoadGrip.FromWetness`). The front axle's grip is the mean of its two wheels', and a wheel with no reading takes the other's (`RoadGrip.FrontAxle`). Each game's surface field maps to these figures in `SurfaceGrips`, from the game's own published list. The grip a game gives is held to 0.05 to 1.5 (`CenteringSettings.GripFor`).

---

## Wheel torque

Vehicle mode's torques are N·m at the rim. The wheel's torque figure turns them into a share of the motor (`WheelTorqueList.For`, read 2026-11-19):

| Model (product ID) | N·m | Source |
|---|---|---|
| Logitech G29 (C24F, C260), G920 (C262), G923 (C266, C267, C26E) | 2.3 | Logitech's store pages name the G923 a "2.3 Nm" wheel, and its Driving Force page the G29 and G920 a "2.3Nm Racing System" |
| Fanatec 0x0020: CSL DD, Gran Turismo DD Pro, ClubSport DD | 15.0 | Fanatec's Wheel Base Torque FAQ (help.fanatec.com article 48812077676177): CSL DD 5, or 8 with the Boost Kit 180, ClubSport DD up to 15. One ID covers all three, and it takes the most of them, since a figure above the wheel's own only makes the forces weaker. |
| Fanatec ClubSport V2.5 (0x0004) | 8.0 | Fanatec's "Which wheel bases have limited torque?" page |
| Fanatec Podium DD1 (0x0006) | 20.0 | The Wheel Base Torque FAQ |
| Fanatec Podium DD2 (0x0007) | 25.0 | The Wheel Base Torque FAQ |

Thrustmaster publishes no figure for the wheels PadForge drives, so none is listed. A wheel with no listed and no entered figure takes `CenteringSettings.UnlistedWheelTorque`, 25 N·m, the most any listed base gives.

---

## What runs where

Each poll, `WheelCentering.Step` (`WheelCentering.cs` line 379) turns the steering axis, the speed and the grip into a `CenteringFrame`: a constant force level from the PC, and a spring, a damper and a friction effect that the wheel's firmware runs, in the writers' 0 to 10000 units.

- **The torque curve** is the constant force, set from the PC each poll, as racing simulators set theirs.
- **Friction** runs in the wheel at a full coefficient under a limit of Friction over the wheel torque. A wheel with no friction effect gets none (`CenteringSettings.FrictionSent`). On a wheel routed through SDL whose driver lists a damper and no friction, the friction is sent as a damper with a full coefficient and a low limit, which is the cast the Linux wheel drivers make.
- **Damping** runs in the wheel's damper, at the least coefficient the firmware has a step for that gives what is asked. A Logitech or Fanatec damper has fifteen steps (new-lg4ff `SCALE_COEFF(k, 4)`, and hid-fanatecff the same). A Thrustmaster's has hundredths. The damper may use the wheel's whole torque. Held to a share of it, a simulated wheel of 2.2 N·m swung 9° past center at every coefficient with the limit at six tenths, and not at all with the limit at the whole.
- **The PC's damping** covers a wheel with no damper, or one the test saw nothing of, and tops up a damper that gives less than asked at its full coefficient. A late damper costs inertia, the damping times the delay, so it is held to `PcDampingShare` (0.3) of the inertia over the delay.
- **The wheel's own spring**, once the Release Test has measured it, carries the steep part near center. It runs only at a coefficient the test measured, the stiffest whose slope is at most `SpringShare` (0.85) of the curve's slope at center, and under a limit where the line first passes the curve (`EnsureSplit`, `LineUnderCurve`). The PC adds the rest.

The torque from the PC and the wheel's spring together never pass the wheel's own limit.

### The stability rule

A force set from the PC arrives late, and a spring that arrives late acts as a spring with negative damping of its stiffness times the delay. So the damping the firmware gives has to exceed the PC part's steepest slope times the delay, by `Margin` (1.5). Where it falls short, the PC part's slope is cut to what the damping carries (`EnsurePcTable`). Friction counts toward it: over a swing of amplitude A at the wheel's own frequency ω it takes out the energy a damper of 4 F / (π A ω) would, counted at a 5° swing (`SteadySwing`).

The delay is the Release Test's measurement, held to 2 to 40 ms (`LeastDelay`, `MostDelay`), or 10 ms for an unmeasured wheel (`UnmeasuredDelay`). An unmeasured wheel's inertia is taken as 0.015 kg·m², a 30 cm rim of about a kilogram with a geared motor behind it, and an unmeasured damper as giving a tenth of the wheel's torque per radian a second at its full coefficient.

When the test has chosen a return ratio, the damping asked is also at least twice that ratio times the square root of the curve's stiffness at center times the inertia, whichever is more. Damping at 100% is that figure. The card's Damping scales it.

### Start, runaway and the guard

- **Start.** The force from the PC waits until the wheel has stayed within `CalmDegrees` (5°) of one place for `CalmMs` (300 ms), then comes in over `SoftStartMs` (1000 ms). `Reset` starts the wait again. `WheelCenteringRuntime.Step` resets the composer when the mode turns on, after a test, and after a gap of more than `StaleMs` (1000 ms) between steps, so a wheel routed through SDL starts softly after an engine restart too.
- **Runaway.** As the force comes in, a wheel that stood more than `RunawayDegrees` (3°) from center when it started, and is now that much farther out on the same side, moving away from center at over `RunawayDegreesPerSecond` (200°/s) read over `MotionMs` (40 ms), stops the PC part. The check runs from a fifth of the ramp until `RunawayTailMs` (300 ms) past its end. A wheel that stood at center is not read, since the force there is less than the wheel's friction either way and only a hand's turn would show. The one false trip in the simulated hands is a wheel at rest 30° out, taken farther out by hand at 400°/s within 1.3 seconds of the start.
- **Oscillation guard.** `OscillationGuard` counts half cycles, reversal to reversal, between 20 and 500 ms long and wider than 0.4°. Eight in a row at a fast pace, or ten at a slow one (half cycles over 150 ms), each within 15% of the run's first full swing in width and time, is a steady swing, and takes the PC's force one step down the ladder 0.5, 0.25, 0.1, 0. A swing that has grown to 1.5 times the first without shrinking, over more than four half cycles, or three wide half cycles in a row (30° or more) at 400°/s or more, goes straight to 0.1. The guard is fed only once the force has started, so a hand's weave during the wait cannot cut it. At 0 the PC's force is off. Only a reset brings the factor back, since a wheel that swung under a force swings again under the same force.

`CenteringFrame.HeldBack` and `CenteringFrame.Stopped` drive the card's two status lines.

---

## Sending a frame

`StepWheelCentering` (`InputManager.Step2.UpdateInputStates.cs` line 1776) reads the device's `PadSetting` into `CenteringSettings.From`, asks `TelemetryHub` for the speed and grip where the settings want them, and steps `ud.Centering`. The steering axis is the device's first. The range is the one PadForge sends the wheel, held to the model's limits, or the Wheel Range setting where the range is left to the wheel. While Vehicle mode runs or a test measures, the Auto Centering Strength spring is set to 0, and while a test runs no game force reaches the wheel.

`WheelCenteringWriter.Apply` (`WheelCenteringWriter.cs` line 223) writes what changed. Each write is a blocking HID report, and the wheel holds what it was last sent. The first frame a wheel gets writes every slot or ID centering uses, a stop to each empty one, as new-lg4ff `lg4ff_init_slots` and hid-fanatecff `ftecff_init_slots` do when they take a wheel, so a killed run's effects are cleared. A Thrustmaster's four IDs are stopped too, since its effects play until stopped (hid-tmt300rs.c `t300rs_play_effect`).

| Wheel | Where centering goes |
|---|---|
| Logitech | Four slots. new-lg4ff keeps the constant force in the first and gives a spring, damper or friction any free one of the other three (`lg4ff_init_slots` and the slot search in `lg4ff_play_effect`). PadForge gives the spring the second, the damper the third and friction the fourth. The centering force is added to the game's in the first (`MergedForce`). A game's own condition effect plays in the first slot, where no constant fits beside it, so while one plays the centering force is a constant in the fourth slot and friction rests (`EffectsBeside`). The slot is stopped between the two. No reference on disk runs a constant force in a slot other than the first, so its level goes at every slot's byte (`LogitechRawHidWriter.WriteConstantForce`, `levelAtEverySlot`). Only the G27, G25, DFGT and DFP have a friction command. The others take friction as a damper, the cast new-lg4ff makes. |
| Fanatec | Five slots by kind: constant, spring, damper, inertia, friction (hid-ftecff.c lines 1023 to 1036). The base sums every slot each tick (`ftecff_timer`). The centering force joins the game's in the first. A game's spring, damper or friction takes its kind's slot while it plays, and centering's effect of that kind rests, then comes back when it ends. `WriteFanatecGameForce` writes the game's condition when it differs from the one the base holds, and the constant force when it changed, so a moving centering force does not resend the game's effect. A game's inertia takes the slot centering never uses, and is disabled when it ends. Spring mode's Auto Centering Strength is a spring in the same slot as Vehicle mode's, since the base has no centering PadForge can set. While it is on the slot is its own, and `SpringSlotWritten` marks Vehicle mode's spring for a rewrite. |
| Thrustmaster | Sixteen effects by ID, the header ID being the effect ID plus one (hid-tmt300rs.c). The game's force has ID 0. Centering has 1 to 4: spring, damper, friction and its own constant force (`ThrustmasterRawHidWriter.CenteringSpring` to `CenteringForce`), so the wheel adds the two forces itself. |

A wheel routed through SDL takes the frame in `ForceFeedbackState.ApplyCentering` (`ForceFeedbackState.cs` line 1145): an infinite constant force on the steering axis (polar east on a wheel that reports two haptic axes), and a spring, a damper and a friction effect as Cartesian +X conditions, the direction the auto-center spring uses. The constant force is rewritten when its level moves by `CenteringLevelStep` (8) or more. These effects are made ahead of the game's force and rumble. An effect the driver refuses is not asked for again until centering lets go, is logged as a `HAPTICDIAG` line, and is left out of `CenteringEffectsOf`, so the next frame is composed without it. A wheel that holds one effect gives it to centering, and the game's force and rumble wait.

A wheel's arrival also matters to centering: a Logitech wheel in its Driving Force mode, or a G923 in its PlayStation mode, is told to switch to its native mode (`LogitechRawHidWriter.SwitchToNativeMode`, after new-lg4ff `lg4ff_handle_multimode_wheel`), and comes back as its own model with its full range.

Over Remote Link the consumer composes the frame and ships it in the wheel frame. `InputService.ApplyRemoteWheel` writes it with the owner's own writer. A wheel routed through SDL on another PC takes no centering.

---

## The Release Test

`ReleaseTest` runs one step per poll inside the wheel's force feedback pass. It owns the wheel while it runs: no game force pushes it, and the test's level is the force. Every push is held to 45% of the wheel's torque (`MostShare`). The steps:

1. **Settle.** Wait for the wheel to rest for 400 ms. After 3 seconds the test ends as *Moving*.
2. **Ramp.** A slow push, at most a quarter of a newton meter a second, toward the side with more room, until the wheel moves 0.5° (or 2.5 counts of a coarse axis). The level gives the wheel's friction, and the way it moved gives the force's sign. A ramp that reaches 1.5 N·m, or the push limit less the step on a weaker wheel, with no motion ends the test as *NoMotion*.
3. **Step.** The ramp's level plus 0.30 N·m (at most 12% of the torque), toward center, for 250 ms or 15°. A free parabola fitted to the angles past the first thirtieth of the travel gives the acceleration in its curvature and the moment the force arrived at its lowest point: the loop's delay, held to 2 to 40 ms. A step that crossed fewer than 150 counts of the axis keeps no delay under 10 ms (`CoarseCounts`).
4. **Coast.** A fifth of a second with no force. The coast's deceleration with the step's acceleration gives the inertia and the friction.
5. **Damper.** The step again with the damper on, at 8/15 and at the full coefficient. The ground the wheel loses against the free step gives the damping at each.
6. **Spring.** A rising push away from center against the spring, at the full, two-thirds and one-third coefficient, strongest first. The motion summed twice over time, fitted by least squares, gives the stiffness with friction and the starting pull folded into a constant.
7. **Search.** On a worker thread, `WheelPlant` lets the measured wheel go from the release angle at return ratios from 0 to 1.5 in tenths. The least ratio whose swing past center is at most 0.5° wins (`NoOvershootDegrees`), else the least within 1° of the best (`NearBestDegrees`). Six simulated wheels end 0.0 to 0.2° past center.
8. **Releases.** The wheel is turned out to the release angle, braked to rest, and let go into centering already at full strength, twice for 2.5 seconds each: first with the wheel's earlier measurement where its force sign matches, else with the sign alone, then with the new one.

Every push stops past 92% of half the range (*NearLock*). The test brakes with the motor and then waits for rest, since a base with little friction would coast to its lock. Rest and first motion are held to the axis's own counts, learned from the least step it shows, so a ten-bit axis that flickers by one count still reads as at rest.

`ReleaseTestDialog` polls the runtime every 50 ms. **Apply** stores `WheelCalibration.Format()` on `UserDevice.WheelCalibration`: a version, 1, and eleven invariant-culture figures separated by semicolons. Another version, or a figure that is no number, reads as no measurement. Stopping the test, by its button or by closing the window, resets the composer, so centering comes back softly.

---

## Settings

The twelve settings are `PadSetting` fields, per device per controller, in the settings checksum: `CenteringMode` ("0" Spring, "1" Vehicle), `CenteringVehicle` ("sedan", "compact", "van", "race", "x1"), `CenteringSpeedSource`, `CenteringFixedSpeed` (km/h whatever the unit shown, empty for the region's default), `CenteringWeight`, `CenteringOnCenter`, `CenteringAssist`, `CenteringDamping`, `CenteringFriction` (hundredths of a N·m, default 30), `CenteringGrip` (0 from the game, 1 dry, 2 wet, 3 snow, 4 ice), `CenteringWheelTorque` (tenths of a N·m, 0 for none entered) and `CenteringWheelRange` (default 900). The fixed speed starts at 97 km/h where speeds read in miles (60 mph) and 100 km/h elsewhere. No macro action touches them.

`WheelCenteringFacts.Of` decides the card. A Logitech, Fanatec or Thrustmaster wheel has both modes by its saved IDs. A wheel routed through SDL needs `InputDeviceType.Driving` and is read from its open device: Vehicle mode needs `SDL_HAPTIC_CONSTANT` (`IsGenericWheelVehicleCapable`) and Spring mode `SDL_HAPTIC_SPRING` (`IsGenericWheelSpringCapable`). The Friction row shows where the facts include a friction effect.

---

## Sources

- Avinash Balachandran and J. Christian Gerdes, "Designing Steering Feel for Steer-by-Wire Vehicles Using Objective Measures," IEEE/ASME Transactions on Mechatronics. The model, the measures, the Stanford X1 and its Table III figures.
- commonroad-vehicle-models 3.0.2 (BSD-3-Clause, Technical University of Munich): the compact, sedan and van parameters and the tire's stiffness per load.
- TUMFTM/global_racetrajectory_optimization (LGPL-3.0): the race car.
- Hans B. Pacejka, *Tire and Vehicle Dynamics*: the pneumatic trail.
- J. Y. Wong, *Theory of Ground Vehicles*, 2nd ed. (1993): the grip figures.
- ISO 13674-1 (the weave test, as the paper states it) and ISO 17288-1 (the steering-release test).
- Logitech's and Fanatec's published torque figures, as listed above.
- new-lg4ff, hid-fanatecff and hid-tmff2: slot and effect layout, read as documentation.

PadForge takes figures from these and ships none of their code. The About page credits them in its Steering feel references row, as do the README and LICENSE.

---

## Related pages

- [Wheel Centering](../features/wheel-centering.md): the user guide for this feature.
- [Wheel Force Feedback Internals](wheel-ffb-internals.md): the vendor writers and the force feedback pass.
- [Game Telemetry Internals](game-telemetry-internals.md): where the speed and the road surface come from.

---

*Last updated for PadForge 6.0.0.*
