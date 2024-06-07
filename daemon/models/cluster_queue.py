from . import connection


def get_record():
    try:
        # initialize cursor
        cursor = connection.cursor()

        # SQL query to get the data
        select_query = """
            SELECT * FROM cluster_queue
            WHERE file_type="image" LIMIT 1;
        """

        # Execute the get records query
        cursor.execute(select_query)

        # get the data
        data = cursor.fetchone()

        # return the response
        if data:
            return {
                "success": True,
                "data": data
            }
        else:
            return {"success": False}
    except Exception as error:
        # return the response
        return {
            "success": False,
            "error": error
        }


def delete_record(file_id):
    try:
        # initialize cursor
        cursor = connection.cursor()

        # SQL query to delete data
        delete_query = """
            DELETE FROM cluster_queue
            WHERE file_id = %s;
        """

        # Execute the delete record query
        cursor.execute(delete_query, (file_id,))

        # save the changes
        connection.commit()

        # return the response
        return {"success": True}

    except Exception as error:
        # return the response
        return {
            "success": False,
            "error": error
        }
