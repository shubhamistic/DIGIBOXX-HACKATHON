from models import db_connection


def create_user_credentials(user_id, email_id, password):
    try:
        # initialize cursor
        cursor = db_connection.cursor()

        # query to insert the record
        insert_query = "INSERT INTO auth (user_id, email_id, password) VALUES (%s, %s, %s)"

        # execute the insert query
        cursor.execute(insert_query, (user_id, email_id, password))

        # save the changes
        db_connection.commit()

        # return the response
        return {"success": True}

    except Exception as error:
        # return the response
        return {
            "success": False,
            "error": error
        }


def read_user_credentials(email_id):
    try:
        # initialize cursor
        cursor = db_connection.cursor()

        # query to get the record
        select_query = "SELECT * FROM auth WHERE email_id=%s"

        # execute the select query
        cursor.execute(select_query, (email_id,))

        # get the data
        rows = cursor.fetchall()

        # close the cursor
        cursor.close()

        # return the response
        return {
            "success": True,
            "data": rows
        }

    except Exception as error:
        # return the response
        return {
            "success": False,
            "error": error
        }
