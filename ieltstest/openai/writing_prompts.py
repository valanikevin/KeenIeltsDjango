

writing_evaluation_prompt = """
Evaluate IELTS Writing Test:

Writing Task: {task} 
Task Question: {question}
Test Taker Answer: {answer}

Provide your response in the JSON format only, in the following keys: overall_band_score (decimal), task_achievement_band_score (decimal), coherence_and_cohesion_band_score (decimal), lexical_resource_band_score (decimal), grammatical_range_accuracy_band_score (decimal), overall_personalized_feedback_suggestions (string/100-200 words), vocabulary_choice_suggestions (Python List 3/4 points/150-250 words).
"""
