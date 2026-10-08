# Lightbar Mirrors Internals

`ChromaLightbarService` and `LightsyncLightbarService` were removed in `0b0c3003`, along with the Dashboard toggles that started them. Their behavior now lives in the per-device peripheral outputs: the Razer Chroma and Logitech LIGHTSYNC rows take a virtual controller's lighting once they are assigned to it. The Chroma REST session moved to the Chroma backend, and the LIGHTSYNC worker moved to the LED SDK backend, which loads the Logitech engine through the same loader. [Peripheral Outputs Internals](peripheral-outputs-internals.md) covers them.

---

*Last updated for PadForge 5.0.0.*
