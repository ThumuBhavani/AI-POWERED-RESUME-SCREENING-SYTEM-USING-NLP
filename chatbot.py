import re

def get_chatbot_response(query, df):
    """
    Simple NLP-based response generator for recruiter queries.
    It searches the DataFrame for candidate-specific info like score, matched skills, etc.
    """
    query = query.lower()
    response = None

    # Extract candidate name if present in query
    candidate_name = None
    for name in df['file']:
        if name.lower() in query:
            candidate_name = name
            break

    # If query contains 'score'
    if 'score' in query and candidate_name:
        score = df.loc[df['file'] == candidate_name, 'score'].values[0]
        response = f"The score for {candidate_name} is {score}."

    # If query contains 'missing skills'
    elif 'missing' in query and candidate_name:
        missing = df.loc[df['file'] == candidate_name, 'missing_skills'].values[0]
        response = f"The missing skills for {candidate_name} are: {missing}."

    # If query contains 'matched skills'
    elif 'matched' in query and candidate_name:
        matched = df.loc[df['file'] == candidate_name, 'matched_skills'].values[0]
        response = f"The matched skills for {candidate_name} are: {matched}."

    # If query contains 'soft skills'
    elif 'soft' in query and candidate_name:
        soft = df.loc[df['file'] == candidate_name, 'soft_skills'].values[0]
        response = f"The soft skills for {candidate_name} are: {soft}."

    # Default response
    if not response:
        response = "Sorry, I couldn't find an answer."

    return response


def answer_query():
    return None