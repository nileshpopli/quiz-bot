
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    if current_question_id is None:
        return True, ""

    try:
        current_question_id = int(current_question_id)
    except ValueError:
        return False, "Invalid question ID."

    if current_question_id < 0 or current_question_id >= len(PYTHON_QUESTION_LIST):
        return False, "Invalid question ID."

    question = PYTHON_QUESTION_LIST[current_question_id]
    correct_answer = question["answer"]

    if answer not in question["options"]:
        return False, "Invalid answer option."

    if "answers" not in session:
        session["answers"] = {}

    session["answers"][current_question_id] = (answer, answer == correct_answer)
    return True, ""


def get_next_question(current_question_id):
    if current_question_id is None:
        next_question_id = 0
    else:
        try:
            current_question_id = int(current_question_id)
            next_question_id = current_question_id + 1
        except ValueError:
            return None, None

    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]["question_text"]
        return next_question, next_question_id
    else:
        return None, None


def generate_final_response(session):
    if "answers" not in session:
        return "No answers recorded."

    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = sum(1 for answer in session["answers"].values() if answer[1])
    score = (correct_answers / total_questions) * 100

    return f"Quiz completed! You got {correct_answers} out of {total_questions} questions right. Your score is {score:.2f}%."
