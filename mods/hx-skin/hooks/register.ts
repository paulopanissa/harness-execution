import type { Register, ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'

type Spec = Parameters<typeof makeColors>[0]

const STORE_KEY = 'skin'
const DEFAULT_SKIN = 'dusk'

// Dusk: Dracula melhorado (menos saturação, contraste AA). Ember: quente. Tide: frio.
const SKINS: Record<string, Spec> = {
  dusk: {
    label: 'HX Dusk',
    roles: { accent: '#bd93f9', danger: '#f07178', success: '#7ee0a1', warning: '#f1c27d', pro: '#ff92d0' },
    dark: { gray: { anchors: { 'surface-0': '#1e1f29', 'surface-1': '#242533', 'surface-2': '#2a2b3a', 'surface-3': '#30313f', 'text-primary': '#ecebf4', 'text-secondary': '#c6c3d9', 'text-muted': '#a29fbb' } } },
    light: { gray: { anchors: { 'surface-0': '#e9e7f1', 'surface-1': '#f0eef7', 'surface-2': '#f7f6fb', 'text-primary': '#22212d', 'text-secondary': '#474559', 'text-muted': '#5d5a73' } } },
  },
  ember: {
    label: 'HX Ember',
    roles: { accent: '#e39b5f', danger: '#e06c6c', success: '#9cc47a', warning: '#e8b64c', pro: '#c79bd8' },
    dark: { gray: { anchors: { 'surface-0': '#1d1a18', 'surface-1': '#24201d', 'surface-2': '#2b2622', 'surface-3': '#322c27', 'text-primary': '#efe6dc', 'text-secondary': '#cdbfb0', 'text-muted': '#a8998a' } } },
    light: { gray: { anchors: { 'surface-0': '#eee6da', 'surface-1': '#f4ede3', 'surface-2': '#faf6ef', 'text-primary': '#2a231d', 'text-secondary': '#51463b', 'text-muted': '#675b4e' } } },
  },
  tide: {
    label: 'HX Tide',
    roles: { accent: '#6cc3d5', danger: '#ec7a7a', success: '#8fd19e', warning: '#e9c46a', pro: '#a99cf0' },
    dark: { gray: { anchors: { 'surface-0': '#1a1f26', 'surface-1': '#20262e', 'surface-2': '#262d36', 'surface-3': '#2c343e', 'text-primary': '#e6edf3', 'text-secondary': '#bfcad5', 'text-muted': '#97a5b3' } } },
    light: { gray: { anchors: { 'surface-0': '#e4eaef', 'surface-1': '#ecf1f5', 'surface-2': '#f5f8fa', 'text-primary': '#1c242c', 'text-secondary': '#3f4c58', 'text-muted': '#55636f' } } },
  },
}

const NAMES = Object.keys(SKINS)

function lookFor(name: string): ThemeSetArgs {
  const spec: Spec = SKINS[name] ?? (SKINS[DEFAULT_SKIN] as Spec)
  return { colors: makeColors(spec).theme }
}

function asSkin(value: unknown): string {
  return typeof value === 'string' && value in SKINS ? value : DEFAULT_SKIN
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'hx-skin',
      description: `Troca a skin HX (${NAMES.join(' | ')})`,
      argumentHint: NAMES.join('|'),
    })
    const set = await $.theme.set(lookFor(asSkin(await $.store.get(STORE_KEY))))
    if (!set.isDrawn) {
      $.ui.status(set.reason)
    }
    return next(e)
  })

  on('command.run', { command: 'hx-skin' }, async ($, e) => {
    const wanted = e.args.trim().toLowerCase()
    if (!wanted) {
      return { text: `Skin atual: ${asSkin(await $.store.get(STORE_KEY))}. Opções: ${NAMES.join(', ')}` }
    }
    if (!(wanted in SKINS)) {
      return { text: `Skin desconhecida: ${wanted}. Opções: ${NAMES.join(', ')}` }
    }
    await $.store.set(STORE_KEY, wanted)
    const set = await $.theme.set(lookFor(wanted))
    return { text: set.isDrawn ? `Skin ${wanted} aplicada.` : `Skin ${wanted} salva; ${set.reason}` }
  })
}
