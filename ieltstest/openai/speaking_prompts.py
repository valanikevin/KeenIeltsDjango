# Speaking Prompt Template

speaking_evaluation_prompt = """
Evaluate Speaking Test:

{data}
"""

speaking_evaluation_prompt1 = """
You should not hesitate to assign a fair score as low as 4.0-7.0 bands if the responses are not satisfactory or do not meet the IELTS criteria. Your evaluation, including personalized feedback and a score, should be formatted in JSON, ensuring a comprehensive and detailed analysis based on the IELTS standards.
"""

speaking_evaluation_prompt2 = """
Provide your response in the JSON format only, in the following keys: overall_band_score (decimal),fluency_and_coherence_bands (decimal), grammatical_range_and_accuracy_bands (decimal) , lexical_resource_bands (decimal), pronunciation_bands (decimal), overall_personalized_feedback_suggestions (string/100-200 words), word_choice_suggestions (Python List 3/4 points/150-250 words).
"""
