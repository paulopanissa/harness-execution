# Skill: game-feel-juice
Valores iniciais; ajuste por playtest. Tudo configurável (não hardcoded).

## Controle
- **Coyote time**: pulo permitido 80–120 ms após sair da borda.
- **Input buffer**: guardar pulo/ataque 100–150 ms e executar quando possível.
- **Pulo variável**: soltar botão → multiplicar velocidade vertical por 0.4–0.5.
- **Gravidade de queda** 1.5–2.5× a de subida; apex hang (gravidade reduzida perto do topo).
- Aceleração/desaceleração separadas; turn-around mais rápido que aceleração.
- Corner correction: empurrar 2–4 px ao bater quina no pulo.

## Impacto
- **Hitstop**: 40–100 ms congelando atacante e alvo (escala com dano). Implementar via escala de tempo local, não `sleep`.
- **Screen shake**: trauma 0–1, offset = trauma² × max; decai por tempo; ruído (Perlin), não random puro.
- Knockback com direção do golpe; i-frames 0.5–1 s com blink.
- Flash branco 1–2 frames no hit (shader/uniform).

## Feedback visual
- Squash & stretch em pulo/aterrisagem (10–20%).
- Partículas no pulo, aterrisagem, hit, morte (via pool).
- Easing (out-back, out-elastic) em UI e coletáveis; nada linear.
- Números de dano/combo com pop + fade.

## Feedback sonoro
- Som para TODA ação do jogador. Variação de pitch ±5–10% em sons repetidos.
- Camadas: ataque + impacto + material. Ducking de música em eventos grandes.
- Limitar vozes simultâneas do mesmo som (2–4).

## Checklist por feature
Entrada responde no mesmo frame? Tem som? Tem partícula/tween? Tem hitstop/shake proporcional? Desligável (acessibilidade: reduzir shake/flash)?
