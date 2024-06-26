from . import get_db


def get_all_records():
    # try:
    # initialize cursor
    db = get_db()
    cursor = db.connection.cursor()

    # SQL query to get the data
    select_query = """
        SELECT * FROM cluster_queue
        WHERE file_type="image";
    """

    # Execute the get records query
    cursor.execute(select_query)

    # get the data
    data = cursor.fetchall()

    # return the response
    if data:
        return {
            "success": True,
            "data": data
        }
    else:
        return {"success": False}
    # except Exception as error:
    #     # return the response
    #     return {
    #         "success": False,
    #         "error": error
    #     }


def insert_record(user_id, file_id, file_type):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to insert data
        insert_query = """
            INSERT INTO cluster_queue (user_id, file_id, file_type)
            VALUES (%s, %s, %s);
        """

        # Execute the insert record query
        cursor.execute(insert_query, (user_id, file_id, file_type))

        # save the changes
        db.connection.commit()

        # return the response
        return {"success": True}

    except Exception as error:
        # return the response
        return {
            "success": False,
            "error": error
        }


def delete_record(file_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to delete data
        delete_query = """
            DELETE FROM cluster_queue
            WHERE file_id = %s;
        """

        # Execute the delete record query
        cursor.execute(delete_query, (file_id,))

        # save the changes
        db.connection.commit()

        # return the response
        return {"success": True}

    except Exception as error:
        # return the response
        return {
            "success": False,
            "error": error
        }
