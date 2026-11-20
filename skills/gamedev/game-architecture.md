# Skill: game-architecture
Decoupling for games. Use the engine/project pattern; this is a reference.

## ECS
- Entity = id. Component = pure data (no logic). System = logic over component queries.
- Systems in a fixed order per phase: input → AI → physics → gameplay → animation → audio → render.
- Contiguous data (arrays/SoA) for cache; no string lookups in the loop.
- Godot: nodes as components + signals; Unity: lean MonoBehaviour or DOTS; Bevy: native ECS.

## State Machine
- State = object/enum with `enter`, `update(dt)`, `exit`, `handle(event)`.
- Explicit transitions in a table; no `if`s scattered over boolean flags.
- Hierarchical (HSM) when states share behavior (e.g. `Grounded` → `Idle|Run`).
- Use for player, AI, UI/menus, game flow (Boot → Menu → Play → Pause → GameOver).

## Event Bus
- Typed events (`PlayerDamaged{amount, source}`), not loose strings.
- The emitter does not know its listeners. Listeners unsubscribe on `exit`/destroy.
- High-frequency (per-frame) events → no bus; read the component directly.
- Event queue processed at a fixed point of the frame for deterministic order.

## Decoupling
- Gameplay does not call render/audio directly → event or a "request" component.
- Design data (stats, waves, drops) in resources/JSON/ScriptableObject, not hardcoded.
- Minimal global services (Audio, Save, Input) via locator/autoload, behind an interface.
- Scene/level loaded from data; spawn via factory + pool.

## Save/Load
- Serialize state, not engine objects. Version the format.
