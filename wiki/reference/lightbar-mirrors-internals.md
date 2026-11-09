# Lightbar Mirrors Internals

`ChromaLightbarService` and `LightsyncLightbarService` were removed in `0b0c3003`, along with the Dashboard toggles that started them. Their behavior now lives in the per-device peripheral outputs: the Razer Chroma and Logitech LIGHTSYNC rows take a virtual controller's lighting once they are assigned to it. The Chroma REST session moved to the Chroma backend, and the LIGHTSYNC worker moved to the LED SDK backend, which loads the Logitech engine through the same loader. [Peripheral Outputs Internals](peripheral-outputs-internals.md) covers them.

The migration of the two toggles into assignments is still `PeripheralSwitchMigration` (`PeripheralSwitchMigration.cs`), unchanged in 5.3.0. What 5.3.0 changed sits in the backends the rows reach: `ChromaBackend`, `LedSdkBackend` and `GameSenseBackend` paint a claim's `KeyFrame` light by light where a device's map has more than one light, and `PeripheralRowKind` gained `AsusAura`, `MsiMysticLight` and `CorsairIcue`, whose rows reach `AuraSdkBackend`, `MysticLightBackend` and `IcueBackend`. [Peripheral Outputs Internals](peripheral-outputs-internals.md#vendor-rows) has the rows and [the SDK routes](peripheral-outputs-internals.md#the-sdk-routes) the backends.

---

*Last updated for PadForge 5.3.0.*
