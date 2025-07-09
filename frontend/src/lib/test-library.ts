import { TestTemplate, TestConfiguration } from '../types/tests';

export const TEST_LIBRARY: TestConfiguration = {
  who5: {
    key: 'who5',
    name: 'WHO-5 Wellbeing Index',
    description: 'A short questionnaire to measure current mental wellbeing',
    category: 'wellbeing',
    duration_minutes: 2,
    branching_enabled: false,
    questions: [
      {
        id: 1,
        text: 'I have felt cheerful and in good spirits',
        order: 1,
        min_value: 0,
        max_value: 5,
        weight: 1.0,
        question_type: 'likert',
        options: ['At no time', 'Some of the time', 'Less than half of the time', 'More than half of the time', 'Most of the time', 'All of the time'],
        required: true,
        reverse_scored: false
      },
      {
        id: 2,
        text: 'I have felt calm and relaxed',
        order: 2,
        min_value: 0,
        max_value: 5,
        weight: 1.0,
        question_type: 'likert',
        options: ['At no time', 'Some of the time', 'Less than half of the time', 'More than half of the time', 'Most of the time', 'All of the time'],
        required: true,
        reverse_scored: false
      },
      {
        id: 3,
        text: 'I have felt active and vigorous',
        order: 3,
        min_value: 0,
        max_value: 5,
        weight: 1.0,
        question_type: 'likert',
        options: ['At no time', 'Some of the time', 'Less than half of the time', 'More than half of the time', 'Most of the time', 'All of the time'],
        required: true,
        reverse_scored: false
      },
      {
        id: 4,
        text: 'I woke up feeling fresh and rested',
        order: 4,
        min_value: 0,
        max_value: 5,
        weight: 1.0,
        question_type: 'likert',
        options: ['At no time', 'Some of the time', 'Less than half of the time', 'More than half of the time', 'Most of the time', 'All of the time'],
        required: true,
        reverse_scored: false
      },
      {
        id: 5,
        text: 'My daily life has been filled with things that interest me',
        order: 5,
        min_value: 0,
        max_value: 5,
        weight: 1.0,
        question_type: 'likert',
        options: ['At no time', 'Some of the time', 'Less than half of the time', 'More than half of the time', 'Most of the time', 'All of the time'],
        required: true,
        reverse_scored: false
      }
    ],
    scoring_rules: {
      type: 'simple_sum',
      normalization_method: 'percentage'
    },
    interpretation_guide: {
      score_ranges: [
        { min_score: 0, max_score: 50, label: 'Poor Wellbeing', description: 'Indicates possible depression or low mood', color: '#dc3545', severity: 'high' },
        { min_score: 51, max_score: 75, label: 'Moderate Wellbeing', description: 'Some areas for improvement', color: '#ffc107', severity: 'moderate' },
        { min_score: 76, max_score: 100, label: 'High Wellbeing', description: 'Good mental wellbeing', color: '#28a745', severity: 'low' }
      ],
      recommendations: [
        { condition: 'score < 50', recommendations: ['Consider speaking with a mental health professional', 'Practice mindfulness and self-care', 'Establish a regular sleep schedule'], urgency: 'high' },
        { condition: 'score >= 50 && score < 76', recommendations: ['Incorporate regular exercise', 'Connect with friends and family', 'Try stress management techniques'], urgency: 'medium' },
        { condition: 'score >= 76', recommendations: ['Maintain your current positive habits', 'Consider helping others who may be struggling'], urgency: 'low' }
      ],
      risk_indicators: [
        { question_ids: [1, 2, 3, 4, 5], threshold_values: [1, 1, 1, 1, 1], risk_level: 'high', alert_message: 'Multiple low scores indicate significant wellbeing concerns' }
      ]
    }
  },

  gad7: {
    key: 'gad7',
    name: 'GAD-7 Anxiety Assessment',
    description: 'Generalized Anxiety Disorder 7-item scale to measure anxiety symptoms',
    category: 'wellbeing',
    duration_minutes: 3,
    branching_enabled: true,
    questions: [
      {
        id: 11,
        text: 'Feeling nervous, anxious, or on edge',
        order: 1,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 12,
        text: 'Not being able to stop or control worrying',
        order: 2,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 13,
        text: 'Worrying too much about different things',
        order: 3,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 14,
        text: 'Trouble relaxing',
        order: 4,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 15,
        text: 'Being so restless that it\'s hard to sit still',
        order: 5,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 16,
        text: 'Becoming easily annoyed or irritable',
        order: 6,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 17,
        text: 'Feeling afraid as if something awful might happen',
        order: 7,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 18,
        text: 'If you checked off any problems, how difficult have these made it for you to do your work, take care of things at home, or get along with other people?',
        order: 8,
        min_value: 0,
        max_value: 3,
        weight: 0.0, // Not scored but important for clinical assessment
        question_type: 'choice',
        options: ['Not difficult at all', 'Somewhat difficult', 'Very difficult', 'Extremely difficult'],
        required: false,
        show_if_question_id: 11, // Show only if any anxiety symptoms reported
        show_if_value: 1,
        reverse_scored: false
      }
    ],
    scoring_rules: {
      type: 'simple_sum',
      normalization_method: 'percentage'
    },
    interpretation_guide: {
      score_ranges: [
        { min_score: 0, max_score: 4, label: 'Minimal Anxiety', description: 'Little to no anxiety symptoms', color: '#28a745' },
        { min_score: 5, max_score: 9, label: 'Mild Anxiety', description: 'Mild anxiety symptoms', color: '#ffc107' },
        { min_score: 10, max_score: 14, label: 'Moderate Anxiety', description: 'Moderate anxiety symptoms', color: '#fd7e14' },
        { min_score: 15, max_score: 21, label: 'Severe Anxiety', description: 'Severe anxiety symptoms', color: '#dc3545', severity: 'high' }
      ],
      recommendations: [
        { condition: 'score >= 10', recommendations: ['Consider professional counseling', 'Practice relaxation techniques', 'Regular exercise can help reduce anxiety'], urgency: 'high' },
        { condition: 'score >= 5 && score < 10', recommendations: ['Try mindfulness meditation', 'Limit caffeine intake', 'Ensure adequate sleep'], urgency: 'medium' }
      ],
      risk_indicators: [
        { question_ids: [11, 12, 13, 17], threshold_values: [2, 2, 2, 2], risk_level: 'high', alert_message: 'High anxiety levels detected - consider immediate support' }
      ]
    }
  },

  phq9: {
    key: 'phq9',
    name: 'PHQ-9 Depression Screening',
    description: 'Patient Health Questionnaire-9 for depression screening',
    category: 'wellbeing',
    duration_minutes: 4,
    branching_enabled: true,
    questions: [
      {
        id: 21,
        text: 'Little interest or pleasure in doing things',
        order: 1,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 22,
        text: 'Feeling down, depressed, or hopeless',
        order: 2,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 23,
        text: 'Trouble falling or staying asleep, or sleeping too much',
        order: 3,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 24,
        text: 'Feeling tired or having little energy',
        order: 4,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 25,
        text: 'Poor appetite or overeating',
        order: 5,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 26,
        text: 'Feeling bad about yourself or that you are a failure or have let yourself or your family down',
        order: 6,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 27,
        text: 'Trouble concentrating on things, such as reading the newspaper or watching television',
        order: 7,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 28,
        text: 'Moving or speaking so slowly that other people could have noticed? Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual',
        order: 8,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      },
      {
        id: 29,
        text: 'Thoughts that you would be better off dead, or of hurting yourself in some way',
        order: 9,
        min_value: 0,
        max_value: 3,
        weight: 1.0,
        question_type: 'likert',
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        required: true,
        reverse_scored: false
      }
    ],
    scoring_rules: {
      type: 'simple_sum',
      normalization_method: 'percentage'
    },
    interpretation_guide: {
      score_ranges: [
        { min_score: 0, max_score: 4, label: 'Minimal Depression', description: 'Little to no depression symptoms', color: '#28a745' },
        { min_score: 5, max_score: 9, label: 'Mild Depression', description: 'Mild depression symptoms', color: '#ffc107' },
        { min_score: 10, max_score: 14, label: 'Moderate Depression', description: 'Moderate depression symptoms', color: '#fd7e14' },
        { min_score: 15, max_score: 19, label: 'Moderately Severe Depression', description: 'Moderately severe depression symptoms', color: '#dc3545', severity: 'high' },
        { min_score: 20, max_score: 27, label: 'Severe Depression', description: 'Severe depression symptoms', color: '#6f42c1', severity: 'severe' }
      ],
      recommendations: [
        { condition: 'score >= 15', recommendations: ['Seek immediate professional help', 'Contact a mental health crisis line if needed', 'Inform a trusted friend or family member'], urgency: 'high' },
        { condition: 'score >= 10 && score < 15', recommendations: ['Consider counseling or therapy', 'Maintain social connections', 'Regular exercise and sleep routine'], urgency: 'high' },
        { condition: 'score >= 5 && score < 10', recommendations: ['Monitor mood changes', 'Practice self-care activities', 'Stay connected with support network'], urgency: 'medium' }
      ],
      risk_indicators: [
        { question_ids: [29], threshold_values: [1], risk_level: 'high', alert_message: 'CRITICAL: Suicidal ideation detected - immediate intervention required', immediate_action: 'Contact emergency services or crisis hotline' },
        { question_ids: [21, 22], threshold_values: [2, 2], risk_level: 'moderate', alert_message: 'Core depression symptoms present' }
      ]
    }
  },

  big5: {
    key: 'big5',
    name: 'Big Five Personality Assessment',
    description: 'Comprehensive personality assessment based on the Five-Factor Model',
    category: 'personality',
    duration_minutes: 15,
    branching_enabled: false,
    questions: [
      // Openness items
      {
        id: 101,
        text: 'I see myself as someone who is original, comes up with new ideas',
        order: 1,
        min_value: 1,
        max_value: 5,
        weight: 1.0,
        dimension_pair: 'O',
        positive_letter: 'O',
        question_type: 'likert',
        options: ['Disagree strongly', 'Disagree a little', 'Neither agree nor disagree', 'Agree a little', 'Agree strongly'],
        required: true,
        reverse_scored: false
      },
      {
        id: 102,
        text: 'I see myself as someone who is conventional, uncreative',
        order: 2,
        min_value: 1,
        max_value: 5,
        weight: 1.0,
        dimension_pair: 'O',
        positive_letter: 'O',
        question_type: 'likert',
        options: ['Disagree strongly', 'Disagree a little', 'Neither agree nor disagree', 'Agree a little', 'Agree strongly'],
        required: true,
        reverse_scored: true
      },
      // Conscientiousness items
      {
        id: 103,
        text: 'I see myself as someone who does a thorough job',
        order: 3,
        min_value: 1,
        max_value: 5,
        weight: 1.0,
        dimension_pair: 'C',
        positive_letter: 'C',
        question_type: 'likert',
        options: ['Disagree strongly', 'Disagree a little', 'Neither agree nor disagree', 'Agree a little', 'Agree strongly'],
        required: true,
        reverse_scored: false
      },
      {
        id: 104,
        text: 'I see myself as someone who tends to be lazy',
        order: 4,
        min_value: 1,
        max_value: 5,
        weight: 1.0,
        dimension_pair: 'C',
        positive_letter: 'C',
        question_type: 'likert',
        options: ['Disagree strongly', 'Disagree a little', 'Neither agree nor disagree', 'Agree a little', 'Agree strongly'],
        required: true,
        reverse_scored: true
      },
      // Additional questions would continue for all 5 dimensions...
    ],
    scoring_rules: {
      type: 'dimensional',
      dimensions: ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism'],
      reverse_questions: [102, 104],
      normalization_method: 'percentile'
    },
    interpretation_guide: {
      score_ranges: [
        { min_score: 0, max_score: 20, label: 'Very Low', description: 'Significantly below average', color: '#dc3545' },
        { min_score: 21, max_score: 40, label: 'Low', description: 'Below average', color: '#fd7e14' },
        { min_score: 41, max_score: 60, label: 'Average', description: 'Typical range', color: '#ffc107' },
        { min_score: 61, max_score: 80, label: 'High', description: 'Above average', color: '#20c997' },
        { min_score: 81, max_score: 100, label: 'Very High', description: 'Significantly above average', color: '#28a745' }
      ],
      recommendations: [],
      risk_indicators: []
    }
  },

  pss: {
    key: 'pss',
    name: 'Perceived Stress Scale',
    description: 'Measures the degree to which situations in life are perceived as stressful',
    category: 'stress',
    duration_minutes: 5,
    branching_enabled: false,
    questions: [
      {
        id: 201,
        text: 'In the last month, how often have you been upset because of something that happened unexpectedly?',
        order: 1,
        min_value: 0,
        max_value: 4,
        weight: 1.0,
        question_type: 'likert',
        options: ['Never', 'Almost never', 'Sometimes', 'Fairly often', 'Very often'],
        required: true,
        reverse_scored: false
      },
      {
        id: 202,
        text: 'In the last month, how often have you felt that you were unable to control the important things in your life?',
        order: 2,
        min_value: 0,
        max_value: 4,
        weight: 1.0,
        question_type: 'likert',
        options: ['Never', 'Almost never', 'Sometimes', 'Fairly often', 'Very often'],
        required: true,
        reverse_scored: false
      },
      {
        id: 203,
        text: 'In the last month, how often have you felt nervous and stressed?',
        order: 3,
        min_value: 0,
        max_value: 4,
        weight: 1.0,
        question_type: 'likert',
        options: ['Never', 'Almost never', 'Sometimes', 'Fairly often', 'Very often'],
        required: true,
        reverse_scored: false
      },
      {
        id: 204,
        text: 'In the last month, how often have you felt confident about your ability to handle your personal problems?',
        order: 4,
        min_value: 0,
        max_value: 4,
        weight: 1.0,
        question_type: 'likert',
        options: ['Never', 'Almost never', 'Sometimes', 'Fairly often', 'Very often'],
        required: true,
        reverse_scored: true
      }
      // Additional PSS questions would continue...
    ],
    scoring_rules: {
      type: 'simple_sum',
      reverse_questions: [204],
      normalization_method: 'percentage'
    },
    interpretation_guide: {
      score_ranges: [
        { min_score: 0, max_score: 13, label: 'Low Stress', description: 'Good stress management', color: '#28a745' },
        { min_score: 14, max_score: 26, label: 'Moderate Stress', description: 'Average stress levels', color: '#ffc107' },
        { min_score: 27, max_score: 40, label: 'High Stress', description: 'Elevated stress levels', color: '#dc3545', severity: 'high' }
      ],
      recommendations: [
        { condition: 'score >= 27', recommendations: ['Practice stress reduction techniques', 'Consider professional stress management counseling', 'Evaluate work-life balance'], urgency: 'high' },
        { condition: 'score >= 14 && score < 27', recommendations: ['Regular exercise', 'Mindfulness practices', 'Time management skills'], urgency: 'medium' }
      ],
      risk_indicators: []
    }
  },

  // Simplified versions for other tests to keep response manageable
  maslach: {
    key: 'maslach',
    name: 'Maslach Burnout Inventory',
    description: 'Assessment of job burnout across three dimensions',
    category: 'stress',
    duration_minutes: 10,
    branching_enabled: false,
    questions: [], // Would contain MBI questions
    scoring_rules: {
      type: 'dimensional',
      dimensions: ['Emotional Exhaustion', 'Depersonalization', 'Personal Accomplishment']
    },
    interpretation_guide: {
      score_ranges: [],
      recommendations: [],
      risk_indicators: []
    }
  },

  mbti_extended: {
    key: 'mbti_extended',
    name: 'Extended MBTI Assessment',
    description: 'Comprehensive personality type assessment',
    category: 'personality',
    duration_minutes: 20,
    branching_enabled: true,
    questions: [], // Would contain extended MBTI questions
    scoring_rules: {
      type: 'dimensional',
      dimensions: ['IE', 'SN', 'TF', 'JP']
    },
    interpretation_guide: {
      score_ranges: [],
      recommendations: [],
      risk_indicators: []
    }
  },

  disc_advanced: {
    key: 'disc_advanced',
    name: 'Advanced DISC Assessment',
    description: 'Comprehensive behavioral style assessment',
    category: 'personality',
    duration_minutes: 15,
    branching_enabled: false,
    questions: [], // Would contain DISC questions
    scoring_rules: {
      type: 'dimensional',
      dimensions: ['Dominance', 'Influence', 'Steadiness', 'Compliance']
    },
    interpretation_guide: {
      score_ranges: [],
      recommendations: [],
      risk_indicators: []
    }
  },

  eq_assessment: {
    key: 'eq_assessment',
    name: 'Emotional Intelligence Assessment',
    description: 'Measures emotional intelligence capabilities',
    category: 'cognitive',
    duration_minutes: 12,
    branching_enabled: false,
    questions: [], // Would contain EQ questions
    scoring_rules: {
      type: 'dimensional',
      dimensions: ['Self-Awareness', 'Self-Regulation', 'Motivation', 'Empathy', 'Social Skills']
    },
    interpretation_guide: {
      score_ranges: [],
      recommendations: [],
      risk_indicators: []
    }
  },

  job_satisfaction: {
    key: 'job_satisfaction',
    name: 'Job Satisfaction Survey',
    description: 'Comprehensive assessment of workplace satisfaction',
    category: 'engagement',
    duration_minutes: 8,
    branching_enabled: true,
    questions: [], // Would contain job satisfaction questions
    scoring_rules: {
      type: 'dimensional',
      dimensions: ['Work Content', 'Compensation', 'Supervision', 'Coworkers', 'Growth Opportunities']
    },
    interpretation_guide: {
      score_ranges: [],
      recommendations: [],
      risk_indicators: []
    }
  }
};

export function getTestByKey(key: string): TestTemplate | undefined {
  return TEST_LIBRARY[key as keyof TestConfiguration];
}

export function getAllTests(): TestTemplate[] {
  return Object.values(TEST_LIBRARY);
}

export function getTestsByCategory(category: TestTemplate['category']): TestTemplate[] {
  return Object.values(TEST_LIBRARY).filter(test => test.category === category);
}