import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Row } from '../types'

// Relative to the session's working directory: run Claude Code from the repo root.
const DIR = '.golemllm'
const QUEUE = `${DIR}/proposals.jsonl`
const DECISIONS = `${DIR}/decisions.jsonl`
const PANE = 'golemllm-proposals'
const POLL_MS = 2000

const rows = atom({ plugin: 'golemllm-proposals', key: 'rows' } as const, [] as Row[], {
  shape: 'rows-1',
})
const toggled = atom({ plugin: 'golemllm-proposals', key: 'toggled' } as const, [] as number[], {
  shape: 'toggled-1',
})

const parse = (text: string) =>
  text
    .split('\n')
    .filter(line => line.trim())
    .map(line => JSON.parse(line))

// A pending row is open unless folded; a decided row is folded unless opened.
const isOpen = (r: Row, flipped: number[]) =>
  (r.decision === 'pending') !== flipped.includes(r.index)

async function readOr(path: string, $: EngineInterface): Promise<string> {
  try {
    return await $.fs.read(path)
  } catch {
    return ''
  }
}

// Rebuilds the rows from both files. Called on start and on each poll.
async function sync($: EngineInterface) {
  const queue = parse(await readOr(QUEUE, $))
  const decided = new Map<number, string>(
    parse(await readOr(DECISIONS, $)).map(d => [d.index, d.decision]),
  )
  const next: Row[] = queue.map((p, i) => ({
    index: i + 1,
    title: p.title,
    reason: p.reason,
    shot: p.reference_shot_ID,
    command: p.proposed_command,
    decision: decided.get(i + 1) ?? 'pending',
  }))
  await update($, rows, () => next)
}

// Records a decision for one proposal. Reads the files again rather than
// trusting the drawing, and only writes a proposal still pending.
async function decide($: EngineInterface, index: number, decision: 'approved' | 'denied') {
  const queue = parse(await readOr(QUEUE, $))
  const decided = parse(await readOr(DECISIONS, $))
  const proposal = queue[index - 1]
  if (!proposal || decided.some(d => d.index === index)) return
  const line = JSON.stringify({ index, decision, time: Date.now() / 1000, proposal }) + '\n'
  await $.fs.write(DECISIONS, (await readOr(DECISIONS, $)) + line)
  // A decided row takes its default fold, so drop any flip made while pending.
  await update($, toggled, list => list.filter(i => i !== index))
  await sync($)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.ui.open({ id: PANE, title: 'GolemLLM proposals', backgroundColor: 'transparent' })
    await sync($)
    $.clock.every(POLL_MS, () => sync($))

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const list = await read($, rows)
    const flipped = await read($, toggled)
    const width = Math.max(20, Math.min(72, (e.viewport?.columns ?? 60) - 6))
    const rule = '─'.repeat(width)
    const wrapped = (text: string) => Math.max(1, Math.ceil(text.length / width))

    // Rows the tree takes, estimated: header, then per proposal its label and,
    // when open, the shot, reason, command and (pending) buttons.
    const height = list.reduce((sum, r) => {
      const open = isOpen(r, flipped)
      const body = open
        ? 1 + wrapped(`Reasoning: ${r.reason}`) + wrapped(`Command: ${r.command}`) + (r.decision === 'pending' ? 1 : 0)
        : 0
      return sum + 2 + body
    }, 1)
    const offset = e.scroll?.offset ?? 0
    const bodyRows = e.scroll?.bodyRows ?? height
    const pending = list.filter(r => r.decision === 'pending').length

    return (
      <Box flexDirection="column">
        {offset > 0 ? (
          <Text color="subtle">▲ {offset} more above</Text>
        ) : (
          <Text color="subtle">{rule}</Text>
        )}
        <Text color="claude">━━ GolemLLM proposals · {pending} pending ━━</Text>
        {list.length === 0 && <Text color="inactive">No proposals in {DIR}.</Text>}
        {list.map(r => {
          const open = isOpen(r, flipped)
          const label = `${open ? '▾' : '▸'} GsP#${r.index} [${r.decision}] ${r.title}`
          return (
            <Box key={`box-${r.index}`} flexDirection="column">
              <Text color="subtle">{'┄'.repeat(width)}</Text>
              <Button
                key={`gsp-${r.index}`}
                label={label}
                variant={r.decision === 'pending' ? 'primary' : 'secondary'}
                onPress={() =>
                  update($, toggled, list =>
                    list.includes(r.index) ? list.filter(i => i !== r.index) : [...list, r.index],
                  )
                }
              >
                {r.decision === 'pending' ? (
                  label
                ) : (
                  <Text color={r.decision === 'approved' ? 'success' : 'error'}>
                    {label}
                  </Text>
                )}
              </Button>
              {open && (
                <Box flexDirection="column">
                  <Text color="subtle">  Reference shot: GM#{r.shot}</Text>
                  <Text color="text">  Reasoning: {r.reason}</Text>
                  <Text color="claude">  Command: {r.command}</Text>
                  {r.decision === 'pending' && (
                    <Box flexDirection="row">
                      <Button key={`approve-${r.index}`} label="Approve" variant="primary"
                        onPress={() => decide($, r.index, 'approved')}>
                        Approve
                      </Button>
                      <Button key={`deny-${r.index}`} label="Deny" onPress={() => decide($, r.index, 'denied')}>
                        Deny
                      </Button>
                    </Box>
                  )}
                </Box>
              )}
            </Box>
          )
        })}
        {offset + bodyRows < height ? (
          <Text color="subtle">▼ more below</Text>
        ) : (
          <Text color="subtle">{rule}</Text>
        )}
      </Box>
    )
  })
}
