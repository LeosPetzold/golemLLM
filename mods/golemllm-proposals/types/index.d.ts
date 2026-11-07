export type Row = {
  index: number;
  title: string;
  reason: string;
  shot: number;
  command: string;
  decision: string;
};

declare module 'claude-code' {
  interface PluginState {
    'golemllm-proposals': {
      rows: Shaped<Row[]>;
      // Indexes the person flipped: pending rows they folded, decided rows they opened.
      toggled: Shaped<number[]>;
    };
  }
}
