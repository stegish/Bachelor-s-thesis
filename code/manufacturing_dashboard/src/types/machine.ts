export interface Machine {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'maintenance';
  utilization: number;
  // … altri campi base
}

export interface MachineMetrics {
  machineId: string;      // assicurati che ci sia per il merge
  efficiency: number;
  runtime: number;
  downtime: number;
  // … metri­che varie
}

// 👇 nuovo
export type MachineWithMetrics = Machine & MachineMetrics;
