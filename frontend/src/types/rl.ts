export interface RLEvaluation {
  final_value: number;
  cumulative_return: number;
  average_reward: number;
  total_turnover: number;
}

export interface RLStrategy {
  name: string;
  final_value: number;
  cumulative_return: number;
  average_reward: number;
  total_turnover: number;
}

export interface RLResponse {
  selected_action: number;
  training_rewards: Record<string, number>;
  validation: RLEvaluation;
  test: RLEvaluation;
  q_learning_validation: RLEvaluation;
  q_learning_test: RLEvaluation;
  strategies: RLStrategy[];
}

export interface RLRequest {
  returns: number[][];
  assets: string[];
  actions: number[][];
  initial_capital?: number;
  transaction_cost_bps?: number;
  risk_free_rate?: number;
}
