# Skill: game-architecture
Desacoplamento para jogos. Use o padrão da engine/projeto; isto é referência.

## ECS
- Entidade = id. Componente = dado puro (sem lógica). Sistema = lógica sobre consultas de componentes.
- Sistemas em ordem fixa por fase: input → AI → física → gameplay → animação → áudio → render.
- Dados contíguos (arrays/SoA) para cache; evitar lookup por string no loop.
- Godot: nós como componentes + sinais; Unity: MonoBehaviour enxuto ou DOTS; Bevy: ECS nativo.

## State Machine
- Estado = objeto/enum com `enter`, `update(dt)`, `exit`, `handle(evento)`.
- Transições explícitas numa tabela; sem `if` espalhado por flags booleanas.
- Hierárquica (HSM) quando estados compartilham comportamento (ex.: `Grounded` → `Idle|Run`).
- Usar para player, IA, UI/menus, fluxo de jogo (Boot → Menu → Play → Pause → GameOver).

## Event Bus
- Eventos tipados (`PlayerDamaged{amount, source}`), não strings soltas.
- Emissor não conhece ouvintes. Ouvintes se desinscrevem no `exit`/destroy.
- Eventos de alta frequência (por frame) → não usar bus; ler componente direto.
- Fila de eventos processada em ponto fixo do frame para ordem determinística.

## Decoupling
- Gameplay não chama render/áudio diretamente → evento ou componente de “pedido”.
- Dados de design (stats, ondas, drops) em recursos/JSON/ScriptableObject, não hardcoded.
- Serviços globais mínimos (Audio, Save, Input) via locator/autoload, com interface.
- Cena/level carregado por dados; spawn via factory + pool.

## Save/Load
- Serializar estado, não objetos da engine. Versionar formato.
