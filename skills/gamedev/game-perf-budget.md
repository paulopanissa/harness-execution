# Skill: game-perf-budget
Goal: stable 60 FPS = 16.6 ms/frame (120 FPS = 8.3 ms). Measure before optimizing.

## Suggested budget (60 FPS)
| Phase | ms |
|---|---|
| Input + gameplay | 3 |
| Physics | 3 |
| AI/pathfinding | 2 |
| Animation | 1.5 |
| Render (CPU) | 4 |
| Audio + UI | 1 |
| Headroom | 2 |

## Zero-alloc in update/tick
- Forbidden in the loop: `new`, array/object literals, closures/lambdas, string concatenation, boxing, LINQ, `GetComponent`/`find` by name, mass `instantiate`/`queue_free`.
- Pre-allocate buffers and reuse them (`clear()` instead of recreating). Temporary vectors as fields.
- Cache references at init. UI strings only when the value changes.
- JS/TS: avoid `map/filter` in the hot loop; indexed `for`; objects with a stable shape.

## Object pooling
- One pool per type, pre-warmed at load; `acquire()/release()` resets state.
- Pool exhausted → grow in batch outside the critical frame or recycle the oldest; log in debug.

## Other rules
- Physics: fixed step; collision layers/masks; broadphase; no per-entity raycast per frame when it can be sliced.
- AI: time-slicing (N agents per frame); async/cached pathfinding.
- Render: batching/instancing, atlases, culling, LOD; minimize draw calls and material switches.
- Update only what is visible/active; sleep distant entities.

## Measuring
- Engine profiler (Godot Monitor/Profiler, Unity Profiler + Memory, Chrome Performance for web).
- Check GC/alloc per frame = 0 in normal gameplay.
- Test on the weakest target hardware; record ms per phase before/after.
