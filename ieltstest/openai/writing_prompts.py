PROMPT0 = """
Assume the role of an IELTS examiner and assess my IELTS writing task using the guidelines detailed below.:
"""

# PROMPT1 = """

# IELTS Writing Task Evaluation Guidelines:
# - COHERENCE AND COHESION: Provide a score out of 9 bands.
# - LEXICAL RESOURCE: Evaluate with a score out of 9 bands.
# - GRAMMATICAL RANGE: Assign a score out of 9 bands.
# - TASK ACHIEVEMENT: Rate this category with a score out of 9 bands.
# - improved_answer: Rewrite my entire response (about 150 words for Task 1 and 250 words for Task 2), making improvements. Feel free to use HTML bootstrap tags to highlight changes visually. For example, if you discover a grammatical error, mark it with a <span> tag and use specific colors to indicate the correction.
# - what_improvements_did_you_made: Explain in 20-50 words the changes you made and why they were necessary.

# """

PROMPT2 = """
Your must provide your entire response in the following python dictionary format only, please replace x.x bands with the evaluation bands:
Response Template:
{
    'overall_score': 'x.x bands',
    'coherence': {
        'overall_coherence_bands': 'x.x bands',
        'logical_structure': 'x.x bands',
        'introduction_conclusion_present': 'x.x bands',
        'supported_main_points': 'x.x bands',
        'accurate_linking_words': 'x.x bands',
        'variety_in_linking_words': 'x.x bands'
    },
    'lexical_resource': {
        'overall_lexical_resource_bands': 'x.x bands',
        'varied_vocabulary': 'x.x bands',
        'accurate_spelling_word_formation': 'x.x bands'
    },
    'grammatical_range': {
        'overall_grammatical_range_bands': 'x.x bands',
        'mix_of_complex_simple_sentences': 'x.x bands',
        'clear_and_correct_grammar': 'x.x bands'
    },
    'task_achievement': {
        'overall_task_achievement_bands': 'x.x bands',
        'complete_response': 'x.x bands',
        'clear_comprehensive_ideas': 'x.x bands',
        'relevant_specific_examples': 'x.x bands',
        'appropriate_word_count': 'x.x bands'
    },
}


"""

PROMPT3 = """
Your response must be structured in a complete dictionary format, beginning with { and ending with }. Make sure to replace the placeholders in the template with the actual evaluation bands for each category. The format should include the overall score, coherence, lexical resource, grammatical range, and task achievement, each represented with specific band scores.
"""

PROMPT4 = """
Please be little bit hard marker so that I do not overestimate myself
"""

PROMPT5 = """
Your must provide your entire response in the following python dictionary format only, please replace x.x bands with the evaluation bands:
Response Template:

{
    'improved_answer': 'Please completely rewrite my original answer ensuring that you meet task word count. The goal of this improved answer is to help me identify potential improvements in vocabulary and other IELTS criteria.',
    'what_improvements_did_you_made': 'Briefly let me know what improvements did you made as compared to my original answer',
}

"""

PROMPT6 = """
Please use HTML tags such as <p>, <span>, etc for improved_answer, and what_improvements_did_you_made
"""
