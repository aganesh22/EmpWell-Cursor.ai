import { 
  TestTemplate, 
  TestQuestion, 
  TestResponse, 
  TestResults, 
  TestSession, 
  BranchingState,
  ScoringRules,
  ScoreRange,
  RecommendationRule,
  RiskIndicator
} from '../types/tests';

export class TestEngine {
  private template: TestTemplate;
  private session: TestSession;

  constructor(template: TestTemplate) {
    this.template = template;
    this.session = {
      current_question: 0,
      responses: [],
      start_time: Date.now(),
      last_activity: Date.now(),
      branching_state: {
        active_conditions: {},
        skipped_questions: [],
        conditional_paths: []
      }
    };
  }

  /**
   * Get the current question, handling branching logic
   */
  getCurrentQuestion(): TestQuestion | null {
    const questions = this.getVisibleQuestions();
    
    if (this.session.current_question >= questions.length) {
      return null; // Test completed
    }

    return questions[this.session.current_question];
  }

  /**
   * Get all questions that should be visible based on branching logic
   */
  getVisibleQuestions(): TestQuestion[] {
    if (!this.template.branching_enabled) {
      return this.template.questions.sort((a, b) => a.order - b.order);
    }

    const allQuestions = this.template.questions.sort((a, b) => a.order - b.order);
    const visibleQuestions: TestQuestion[] = [];

    for (const question of allQuestions) {
      if (this.shouldShowQuestion(question)) {
        visibleQuestions.push(question);
      } else {
        this.session.branching_state.skipped_questions.push(question.id);
      }
    }

    return visibleQuestions;
  }

  /**
   * Determine if a question should be shown based on branching conditions
   */
  private shouldShowQuestion(question: TestQuestion): boolean {
    // If no branching condition, always show
    if (!question.show_if_question_id || question.show_if_value === undefined) {
      return true;
    }

    // Find the response to the condition question
    const conditionResponse = this.session.responses.find(
      r => r.question_id === question.show_if_question_id
    );

    if (!conditionResponse) {
      return false; // Condition question not answered yet
    }

    // Check if condition is met
    return this.evaluateBranchingCondition(conditionResponse.value, question.show_if_value);
  }

  /**
   * Evaluate branching condition based on question type and value
   */
  private evaluateBranchingCondition(responseValue: number | string, conditionValue: number): boolean {
    if (typeof responseValue === 'string') {
      return parseInt(responseValue) >= conditionValue;
    }
    return responseValue >= conditionValue;
  }

  /**
   * Answer the current question and advance to next
   */
  answerQuestion(response: number | string, responseTimeMs?: number): boolean {
    const currentQuestion = this.getCurrentQuestion();
    if (!currentQuestion) {
      return false; // No more questions
    }

    // Validate response
    if (!this.validateResponse(currentQuestion, response)) {
      throw new Error('Invalid response for question');
    }

    // Record response
    const testResponse: TestResponse = {
      question_id: currentQuestion.id,
      value: response,
      response_time_ms: responseTimeMs,
      skipped: false
    };

    this.session.responses.push(testResponse);
    this.session.last_activity = Date.now();

    // Update branching state
    this.updateBranchingState(currentQuestion, response);

    // Advance to next question
    this.session.current_question++;

    return true;
  }

  /**
   * Skip the current question (if allowed)
   */
  skipQuestion(): boolean {
    const currentQuestion = this.getCurrentQuestion();
    if (!currentQuestion || currentQuestion.required) {
      return false; // Cannot skip required questions
    }

    const testResponse: TestResponse = {
      question_id: currentQuestion.id,
      value: 0, // Default value for skipped
      skipped: true
    };

    this.session.responses.push(testResponse);
    this.session.current_question++;
    this.session.last_activity = Date.now();

    return true;
  }

  /**
   * Validate a response against question constraints
   */
  private validateResponse(question: TestQuestion, response: number | string): boolean {
    if (typeof response === 'string') {
      // For choice questions, validate against options
      if (question.question_type === 'choice' && question.options) {
        const index = parseInt(response);
        return index >= 0 && index < question.options.length;
      }
      return true;
    }

    // For numeric responses
    return response >= question.min_value && response <= question.max_value;
  }

  /**
   * Update branching state after answering a question
   */
  private updateBranchingState(question: TestQuestion, response: number | string): void {
    this.session.branching_state.active_conditions[question.id] = response;

    // Check if this response affects future questions
    const affectedQuestions = this.template.questions.filter(
      q => q.show_if_question_id === question.id
    );

    for (const affectedQ of affectedQuestions) {
      const pathKey = `${question.id}->${affectedQ.id}`;
      if (this.evaluateBranchingCondition(response, affectedQ.show_if_value || 0)) {
        this.session.branching_state.conditional_paths.push(pathKey);
      }
    }
  }

  /**
   * Go back to previous question (if allowed)
   */
  previousQuestion(): boolean {
    if (this.session.current_question <= 0) {
      return false; // Already at first question
    }

    this.session.current_question--;
    
    // Remove the response for the question we're going back to
    const questionToRevert = this.getVisibleQuestions()[this.session.current_question];
    if (questionToRevert) {
      this.session.responses = this.session.responses.filter(
        r => r.question_id !== questionToRevert.id
      );
      
      // Update branching state
      delete this.session.branching_state.active_conditions[questionToRevert.id];
    }

    this.session.last_activity = Date.now();
    return true;
  }

  /**
   * Check if test is complete
   */
  isComplete(): boolean {
    const visibleQuestions = this.getVisibleQuestions();
    const requiredQuestions = visibleQuestions.filter(q => q.required);
    const answeredRequired = requiredQuestions.filter(q => 
      this.session.responses.some(r => r.question_id === q.id && !r.skipped)
    );

    return answeredRequired.length === requiredQuestions.length;
  }

  /**
   * Get test progress (0-100)
   */
  getProgress(): number {
    const visibleQuestions = this.getVisibleQuestions();
    if (visibleQuestions.length === 0) return 100;
    
    return Math.round((this.session.current_question / visibleQuestions.length) * 100);
  }

  /**
   * Calculate test results with advanced scoring
   */
  calculateResults(): TestResults {
    if (!this.isComplete()) {
      throw new Error('Cannot calculate results for incomplete test');
    }

    const scoringRules = this.template.scoring_rules;
    const interpretationGuide = this.template.interpretation_guide;

    let results: TestResults;

    switch (scoringRules.type) {
      case 'simple_sum':
        results = this.calculateSimpleSum(scoringRules, interpretationGuide);
        break;
      case 'weighted_sum':
        results = this.calculateWeightedSum(scoringRules, interpretationGuide);
        break;
      case 'dimensional':
        results = this.calculateDimensionalScore(scoringRules, interpretationGuide);
        break;
      case 'categorical':
        results = this.calculateCategoricalScore(scoringRules, interpretationGuide);
        break;
      default:
        throw new Error(`Unsupported scoring type: ${scoringRules.type}`);
    }

    // Add risk assessment
    results.risk_level = this.assessRisk(interpretationGuide.risk_indicators);
    results.follow_up_suggested = results.risk_level === 'high' || results.normalized_score < 50;

    return results;
  }

  /**
   * Calculate simple sum score
   */
  private calculateSimpleSum(rules: ScoringRules, guide: any): TestResults {
    let rawScore = 0;
    const maxPossibleScore = this.template.questions.reduce((sum, q) => sum + q.max_value, 0);

    for (const response of this.session.responses) {
      if (response.skipped) continue;
      
      const question = this.template.questions.find(q => q.id === response.question_id);
      if (!question || question.weight === 0) continue;

      let value = typeof response.value === 'string' ? parseInt(response.value) : response.value;
      
      // Handle reverse scoring
      if (question.reverse_scored) {
        value = question.max_value - value + question.min_value;
      }

      rawScore += value * question.weight;
    }

    const normalizedScore = rules.normalization_method === 'percentage' 
      ? (rawScore / maxPossibleScore) * 100
      : rawScore;

    const interpretation = this.getInterpretation(normalizedScore, guide.score_ranges);
    const recommendations = this.getRecommendations(normalizedScore, guide.recommendations);

    return {
      raw_score: rawScore,
      normalized_score: normalizedScore,
      interpretation: interpretation.label,
      detailed_feedback: interpretation.description,
      recommendations,
      risk_level: 'low', // Will be updated by assessRisk
      follow_up_suggested: false,
      percentile_rank: this.calculatePercentileRank(normalizedScore),
      comparison_group: 'General Population'
    };
  }

  /**
   * Calculate weighted sum score
   */
  private calculateWeightedSum(rules: ScoringRules, guide: any): TestResults {
    // Similar to simple sum but respects individual question weights more explicitly
    return this.calculateSimpleSum(rules, guide);
  }

  /**
   * Calculate dimensional scores (e.g., Big Five, DISC)
   */
  private calculateDimensionalScore(rules: ScoringRules, guide: any): TestResults {
    const dimensionScores: Record<string, number> = {};
    const dimensions = rules.dimensions || [];

    // Initialize dimension scores
    for (const dimension of dimensions) {
      dimensionScores[dimension] = 0;
    }

    // Calculate scores for each dimension
    for (const response of this.session.responses) {
      if (response.skipped) continue;

      const question = this.template.questions.find(q => q.id === response.question_id);
      if (!question || !question.dimension_pair) continue;

      let value = typeof response.value === 'string' ? parseInt(response.value) : response.value;
      
      if (question.reverse_scored) {
        value = question.max_value - value + question.min_value;
      }

      const dimension = question.dimension_pair;
      if (dimensionScores.hasOwnProperty(dimension)) {
        dimensionScores[dimension] += value * question.weight;
      }
    }

    // Normalize dimension scores
    const maxScore = Math.max(...Object.values(dimensionScores));
    const dominantDimension = Object.keys(dimensionScores).find(
      key => dimensionScores[key] === maxScore
    ) || 'Unknown';

    const overallScore = Object.values(dimensionScores).reduce((sum, score) => sum + score, 0) / dimensions.length;

    return {
      raw_score: overallScore,
      normalized_score: (overallScore / 5) * 100, // Assuming 5-point scale
      dimension_scores: dimensionScores,
      interpretation: `Dominant trait: ${dominantDimension}`,
      detailed_feedback: this.generateDimensionalFeedback(dimensionScores),
      recommendations: this.getDimensionalRecommendations(dimensionScores),
      risk_level: 'low',
      follow_up_suggested: false
    };
  }

  /**
   * Calculate categorical score (e.g., personality types)
   */
  private calculateCategoricalScore(rules: ScoringRules, guide: any): TestResults {
    // Implementation would depend on specific categorical logic
    return this.calculateDimensionalScore(rules, guide);
  }

  /**
   * Get interpretation based on score ranges
   */
  private getInterpretation(score: number, ranges: ScoreRange[]): ScoreRange {
    for (const range of ranges) {
      if (score >= range.min_score && score <= range.max_score) {
        return range;
      }
    }
    
    // Fallback
    return {
      min_score: 0,
      max_score: 100,
      label: 'Unknown',
      description: 'Score interpretation not available',
      color: '#6c757d'
    };
  }

  /**
   * Get recommendations based on score and rules
   */
  private getRecommendations(score: number, rules: RecommendationRule[]): string[] {
    const recommendations: string[] = [];

    for (const rule of rules) {
      if (this.evaluateCondition(rule.condition, score)) {
        recommendations.push(...rule.recommendations);
      }
    }

    return recommendations;
  }

  /**
   * Evaluate condition string (simple implementation)
   */
  private evaluateCondition(condition: string, score: number): boolean {
    try {
      // Replace 'score' with actual value and evaluate
      // This is a simplified implementation - production would use a proper expression evaluator
      const expression = condition.replace(/score/g, score.toString());
      return eval(expression);
    } catch {
      return false;
    }
  }

  /**
   * Assess risk level based on indicators
   */
  private assessRisk(indicators: RiskIndicator[]): 'low' | 'moderate' | 'high' {
    let highestRisk: 'low' | 'moderate' | 'high' = 'low';

    for (const indicator of indicators) {
      const relevantResponses = this.session.responses.filter(
        r => indicator.question_ids.includes(r.question_id) && !r.skipped
      );

      // Check if risk threshold is met
      let riskTriggered = false;
      for (let i = 0; i < relevantResponses.length; i++) {
        const response = relevantResponses[i];
        const threshold = indicator.threshold_values[i] || indicator.threshold_values[0];
        
        const value = typeof response.value === 'string' ? parseInt(response.value) : response.value;
        if (value >= threshold) {
          riskTriggered = true;
          break;
        }
      }

      if (riskTriggered) {
        if (indicator.risk_level === 'high') {
          return 'high'; // Immediate return for high risk
        } else if (indicator.risk_level === 'moderate' && highestRisk === 'low') {
          highestRisk = 'moderate';
        }
      }
    }

    return highestRisk;
  }

  /**
   * Calculate percentile rank (simplified)
   */
  private calculatePercentileRank(score: number): number {
    // This would typically use normative data
    // For now, use a simple normal distribution approximation
    return Math.round(score);
  }

  /**
   * Generate feedback for dimensional scores
   */
  private generateDimensionalFeedback(scores: Record<string, number>): string {
    const sortedDimensions = Object.entries(scores)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3); // Top 3 dimensions

    return `Your strongest traits are: ${sortedDimensions.map(([dim, score]) => 
      `${dim} (${score.toFixed(1)})`).join(', ')}`;
  }

  /**
   * Get recommendations for dimensional scores
   */
  private getDimensionalRecommendations(scores: Record<string, number>): string[] {
    const recommendations: string[] = [];
    
    // Add dimension-specific recommendations based on scores
    Object.entries(scores).forEach(([dimension, score]) => {
      if (score > 4.0) {
        recommendations.push(`Your high ${dimension} is a strength - continue leveraging this trait`);
      } else if (score < 2.0) {
        recommendations.push(`Consider developing your ${dimension} skills for better balance`);
      }
    });

    return recommendations;
  }

  /**
   * Get session data for persistence
   */
  getSession(): TestSession {
    return { ...this.session };
  }

  /**
   * Restore session from saved data
   */
  restoreSession(session: TestSession): void {
    this.session = { ...session };
  }

  /**
   * Get test metadata
   */
  getMetadata() {
    return {
      key: this.template.key,
      name: this.template.name,
      description: this.template.description,
      category: this.template.category,
      duration_minutes: this.template.duration_minutes,
      total_questions: this.template.questions.length,
      branching_enabled: this.template.branching_enabled
    };
  }
}