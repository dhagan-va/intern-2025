export interface Status {
  running: boolean;
  rps: number;
  transaction: number;
  threads: number;
  endpoint: string;
}

export interface Stats {
  total_requests: number;
  average_latency: number;
  status_codes: Record<string, number>;
  successful_requests: number;
  failed_requests: number;
  current_rps: number;
  timestamp?: string;
}
