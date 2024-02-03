def unbond_keys_except_users(instance, model):
    survey = instance.survey
    question = instance.question
    following_question = instance.following_question
    # открепление связей со старого объекта
    instance.survey = None
    instance.question = None
    instance.following_question = None
    instance.save()
    # Создание нового объекта Answer и прикрепление к связям старого объекта
    new_answer = model.objects.create(
        survey=survey,
        question=question,
        following_question=following_question,
        text=instance.text,
        is_archived=instance.is_archived,
    )
    # Пометить старый объект как заархивированный
    instance.is_archived = True
    instance.save()
    return


def parse_sql_result(sql_result):
    parsed_result = {
        'participants': sql_result[0],
        'questions': []
    } 

    for question in sql_result[1]:
        parsed_question = {
            'pk': question[0],
            'text': question[1],
            'amount_of_answers': question[2],
            'percent': question[3],
            'rank': question[4],
            'answers': []
        }

        for answer in sql_result[2]:
            if answer[0] == question[0]:
                parsed_answer = {
                    'pk': answer[1],
                    'text': answer[2],
                    'answered_amount': answer[3],
                    'percent': answer[4]
                }
                parsed_question['answers'].append(parsed_answer)

        parsed_result['questions'].append(parsed_question)

    return(parsed_result)