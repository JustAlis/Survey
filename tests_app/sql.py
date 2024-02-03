from django.db import connection


def sql_get_survey_statistics(survey_pk):
    query_1 = """
        SELECT 
            COUNT(DISTINCT ua.user_pk) AS participants 
        FROM 
            tests_app_usersanswers ua
        JOIN 
            tests_app_question q 
        ON 
            ua.question_pk = q.id 
        WHERE 
            q.survey_id = %s
    """
    query_2 = """
        SELECT
            q.id AS question_id,
            q.text AS question,
            COUNT(DISTINCT ua.user_pk) AS answers_count,
            ROUND(COUNT(DISTINCT ua.user_pk) * 100.0 / %s, 2) || "%%" AS percentage,
            DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT ua.user_pk) DESC) AS rank,
            q.is_archived
        FROM
            tests_app_question q
        LEFT JOIN
            tests_app_usersanswers ua ON q.id = ua.question_pk
        WHERE
            q.survey_id = %s AND
            q.is_archived = 0
        GROUP BY
            q.id
        ORDER BY
            answers_count DESC;
    """
    query_3 = """
        SELECT
            q.id AS question_id,
            a.id AS answer_id,
            a.text AS answer,
            COUNT(DISTINCT ua.user_pk) AS answers_count,
            ROUND(COUNT(DISTINCT ua.user_pk) * 100.0 / total_users.total_users_count, 2) || '%%' AS percentage,
            q.is_archived,
            a.is_archived
        FROM
            tests_app_question q
        JOIN
            tests_app_answer a 
        ON 
            q.id = a.question_id
        LEFT JOIN
            tests_app_usersanswers ua 
        ON 
            q.id = ua.question_pk 
        AND 
            a.id = ua.answer_pk
        JOIN 
            (SELECT
                q.id AS question_id,
                COUNT(DISTINCT ua.user_pk) AS total_users_count
            FROM
                tests_app_question q
            LEFT JOIN
                tests_app_usersanswers ua 
            ON 
                q.id = ua.question_pk
            WHERE
                q.survey_id = %s
            GROUP BY
                q.id
            ) AS total_users 
        ON 
            q.id = total_users.question_id
        WHERE
            q.survey_id = %s AND
            q.is_archived = 0 AND
            a.is_archived = 0

        GROUP BY
            q.id, 
            a.id
        ORDER BY
            q.id, 
            answers_count DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query_1, [survey_pk])
        row = cursor.fetchone()
        participants = row[0]

        cursor.execute(query_2, (participants, survey_pk))
        questions_raw_data = cursor.fetchall()

        cursor.execute(query_3, (survey_pk, survey_pk))
        answers_raw_data = cursor.fetchall()
        
    return [participants, questions_raw_data, answers_raw_data]

