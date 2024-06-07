from . import get_db


def get_user_cluster_info(user_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to get the records
        select_query = f"""
            SELECT * FROM user_cluster_{user_id};
        """

        # Execute the get records query
        cursor.execute(select_query)

        # get the data
        rows = cursor.fetchall()

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
