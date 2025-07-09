export interface TestQuestion {
  id: number;
  text: string;
  order: number;
  min_value: number;
  max_value: number;
  weight: number;
  dimension_pair?: string;
  positive_letter?: string;
  show_if_question_id?: number;
  show_if_value?: number;
  question_type: 'likert' | 'boolean' | 'choice' | 'scale';
  options?: string[];
  reverse_scored?: boolean;
  required: boolean;
}

export interface TestTemplate {
  key: string;
  name: string;
  description?: string;
  category: 'wellbeing' | 'personality' | 'cognitive' | 'stress' | 'engagement';
  duration_minutes: number;
  questions: TestQuestion[];
  scoring_rules: ScoringRules;
  interpretation_guide: InterpretationGuide;
  branching_enabled: boolean;
}

export interface ScoringRules {
  type: 'simple_sum' | 'weighted_sum' | 'dimensional' | 'categorical';
  dimensions?: string[];
  reverse_questions?: number[];
  scoring_formula?: string;
  normalization_method?: 'percentage' | 'z_score' | 'percentile';
}

export interface InterpretationGuide {
  score_ranges: ScoreRange[];
  recommendations: RecommendationRule[];
  risk_indicators: RiskIndicator[];
}

export interface ScoreRange {
  min_score: number;
  max_score: number;
  label: string;
  description: string;
  color: string;
  severity?: 'low' | 'moderate' | 'high' | 'severe';
}

export interface RecommendationRule {
  condition: string;
  recommendations: string[];
  resources?: number[];
  urgency: 'low' | 'medium' | 'high';
}

export interface RiskIndicator {
  question_ids: number[];
  threshold_values: number[];
  risk_level: 'low' | 'moderate' | 'high';
  alert_message: string;
  immediate_action?: string;
}

export interface TestAttempt {
  id: number;
  template_key: string;
  user_id: number;
  started_at: string;
  completed_at?: string;
  responses: TestResponse[];
  results?: TestResults;
  status: 'in_progress' | 'completed' | 'abandoned';
}

export interface TestResponse {
  question_id: number;
  value: number | string;
  response_time_ms?: number;
  skipped?: boolean;
}

export interface TestResults {
  raw_score: number;
  normalized_score: number;
  dimension_scores?: Record<string, number>;
  interpretation: string;
  detailed_feedback: string;
  recommendations: string[];
  risk_level: 'low' | 'moderate' | 'high';
  follow_up_suggested: boolean;
  percentile_rank?: number;
  comparison_group?: string;
}

export interface TestSession {
  current_question: number;
  responses: TestResponse[];
  start_time: number;
  last_activity: number;
  branching_state: BranchingState;
}

export interface BranchingState {
  active_conditions: Record<number, any>;
  skipped_questions: number[];
  conditional_paths: string[];
}

// Pre-defined test configurations
export interface TestConfiguration {
  who5: TestTemplate;
  gad7: TestTemplate;
  phq9: TestTemplate;
  pss: TestTemplate;
  maslach: TestTemplate;
  big5: TestTemplate;
  mbti_extended: TestTemplate;
  disc_advanced: TestTemplate;
  eq_assessment: TestTemplate;
  job_satisfaction: TestTemplate;
}

export type TestKey = keyof TestConfiguration;