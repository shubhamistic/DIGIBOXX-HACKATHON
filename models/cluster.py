from . import get_db


def get_specific_cluster_info(user_id, cluster_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to get the records
        select_query = f"""
            SELECT * FROM user_cluster_{user_id}
            WHERE cluster_id=%s;
        """

        # Execute the get records query
        cursor.execute(select_query, (cluster_id,))

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


def get_cluster_info(user_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to get the records
        select_query = f"""
            SELECT * FROM user_cluster_{user_id}
            WHERE is_identity=TRUE;
        """

        # Execute the get records query
        cursor.execute(select_query)

        # get the data
        data = cursor.fetchall()

        # return the response
        return {
            "success": True,
            "data": data
        }

    except Exception as error:
        # return the response
        return {
            "success": False,
            "error": error
        }


def update_user_cluster_name(user_id, cluster_id, cluster_name):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to update the records
        update_query = f"""
            UPDATE user_cluster_{user_id}
            SET cluster_name = %s
            WHERE cluster_id = %s AND is_identity = TRUE
        """

        # execute the insert query
        cursor.execute(update_query, (cluster_name, cluster_id))

        # save the changes
        db.connection.commit()

        # return the response
        return {"success": True}
    except Exception as error:
        # return the response
        return {
            "success": False,
            "error": str(error)
        }
