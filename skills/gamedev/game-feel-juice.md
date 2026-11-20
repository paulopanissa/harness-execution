# Skill: game-feel-juice
Starting values; tune by playtest. Everything configurable (not hardcoded).

## Control
- **Coyote time**: jump allowed 80–120 ms after leaving the edge.
- **Input buffer**: store jump/attack for 100–150 ms and run it when possible.
- **Variable jump**: releasing the button → multiply vertical velocity by 0.4–0.5.
- **Fall gravity** 1.5–2.5× the rising gravity; apex hang (reduced gravity near the top).
- Separate acceleration/deceleration; turn-around faster than acceleration.
- Corner correction: nudge 2–4 px when clipping a corner on a jump.

## Impact
- **Hitstop**: 40–100 ms freezing attacker and target (scales with damage). Implement via local time scale, not `sleep`.
- **Screen shake**: trauma 0–1, offset = trauma² × max; decays over time; noise (Perlin), not pure random.
- Knockback along the hit direction; i-frames 0.5–1 s with blink.
- White flash for 1–2 frames on hit (shader/uniform).

## Visual feedback
- Squash & stretch on jump/landing (10–20%).
- Particles on jump, landing, hit, death (via pool).
- Easing (out-back, out-elastic) on UI and collectibles; nothing linear.
- Damage/combo numbers with pop + fade.

## Audio feedback
- A sound for EVERY player action. Pitch variation ±5–10% on repeated sounds.
- Layers: attack + impact + material. Duck the music on big events.
- Limit simultaneous voices of the same sound (2–4).

## Per-feature checklist
Does input respond on the same frame? Has sound? Has particle/tween? Has proportional hitstop/shake? Can it be turned off (accessibility: reduce shake/flash)?
