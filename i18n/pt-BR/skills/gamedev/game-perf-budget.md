# Skill: game-perf-budget
Meta: 60 FPS estável = 16.6 ms/frame (120 FPS = 8.3 ms). Medir antes de otimizar.

## Budget sugerido (60 FPS)
| Fase | ms |
|---|---|
| Input + gameplay | 3 |
| Física | 3 |
| IA/pathfinding | 2 |
| Animação | 1.5 |
| Render (CPU) | 4 |
| Áudio + UI | 1 |
| Folga | 2 |

## Zero-alloc no update/tick
- Proibido no loop: `new`, literais de array/objeto, closures/lambdas, concatenação de string, boxing, LINQ, `GetComponent`/`find` por nome, `instantiate`/`queue_free` em massa.
- Pré-alocar buffers e reutilizar (`clear()` em vez de recriar). Vetores temporários como campos.
- Cache de referências no init. Strings de UI só ao mudar valor.
- JS/TS: evitar `map/filter` no loop quente; `for` indexado; objetos com forma estável.

## Object pooling
- Pool por tipo, tamanho pré-aquecido no load; `acquire()/release()` reseta estado.
- Pool esgotado → expandir em lote fora do frame crítico ou reciclar o mais antigo; logar em debug.

## Outras regras
- Física: passo fixo; camadas/máscaras de colisão; broadphase; sem raycast por entidade por frame se dá para fatiar.
- IA: time-slicing (N agentes por frame); pathfinding assíncrono/cacheado.
- Render: batching/instancing, atlas, culling, LOD; minimizar draw calls e trocas de material.
- Update só do que está visível/ativo; dormir entidades distantes.

## Medição
- Profiler da engine (Godot Monitor/Profiler, Unity Profiler + Memory, Chrome Performance para web).
- Checar GC/alloc por frame = 0 em gameplay normal.
- Testar no hardware-alvo mais fraco; registrar ms por fase antes/depois.
