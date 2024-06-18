from . import get_db


def create_user_cluster_table(user_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # query to create a new table if not exists in MySQL database
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS user_cluster_{user_id} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cluster_id CHAR(36),
                file_id CHAR(36),
                x1 INT, y1 INT, x2 INT,  y2 INT,
                matched_score INT,
                cluster_name VARCHAR(30),
                is_identity BOOLEAN,
                UNIQUE (cluster_id, file_id)
            );
        """

        # Execute the creation table query
        cursor.execute(create_table_query)

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


def insert_user_cluster_record(user_id, cluster_id, file_id, coords, matched_score, cluster_name=None, is_identity=False):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # query to insert the record in MySQL database
        insert_query = f"""
            INSERT INTO user_cluster_{user_id} (cluster_id, file_id, x1, y1, x2, y2, matched_score, cluster_name, is_identity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        x1, y1, x2, y2 = coords
        # Execute the insert table query
        cursor.execute(insert_query, (cluster_id, file_id, x1, y1, x2, y2, matched_score, cluster_name, is_identity))

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


def get_user_identity_cluster_info(user_id):
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


def get_identity_cluster_file_info(user_id, file_id, cluster_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to get the records
        select_query = f"""
            SELECT * FROM user_cluster_{user_id}
            WHERE cluster_id=%s AND file_id=%s AND is_identity=TRUE;
        """

        # Execute the get records query
        cursor.execute(select_query, (cluster_id, file_id))

        # get the data
        data = cursor.fetchone()

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


def get_file_cluster_info(user_id, file_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to get the records
        select_query = f"""
            SELECT * FROM user_cluster_{user_id}
            WHERE file_id=%s;
        """

        # Execute the get records query
        cursor.execute(select_query, (file_id,))

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


def update_file_cluster(user_id, cluster_id, file_id, target_cluster_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to update the records
        update_query = f"""
            UPDATE user_cluster_{user_id}
            SET cluster_id = %s
            WHERE cluster_id = %s AND file_id = %s;
        """

        # execute the insert query
        cursor.execute(update_query, (target_cluster_id, cluster_id, file_id))

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


def update_matched_score(user_id, cluster_id, file_id, matched_score):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to update the records
        update_query = f"""
            UPDATE user_cluster_{user_id}
            SET matched_score = %s
            WHERE cluster_id = %s AND file_id = %s;
        """

        # execute the insert query
        cursor.execute(update_query, (matched_score, cluster_id, file_id))

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


def update_is_identity_true_in_lowest_match_score(user_id, cluster_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to update the records
        update_query = f"""
            UPDATE user_cluster_{user_id} AS u
            JOIN (
                SELECT file_id
                FROM user_cluster_{user_id}
                WHERE cluster_id = %s
                ORDER BY matched_score
                LIMIT 1
            ) AS sub ON u.file_id = sub.file_id
            SET u.is_identity = TRUE;
        """

        # execute the update query
        cursor.execute(update_query, (cluster_id,))

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


def update_cluster_identity(user_id, cluster_id, file_id, identity):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to update the records
        update_query = f"""
            UPDATE user_cluster_{user_id}
            SET is_identity = %s
            WHERE cluster_id = %s AND file_id = %s;
        """

        # execute the update query
        cursor.execute(update_query, (identity, cluster_id, file_id))

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


def delete_file_existence_from_cluster(user_id, file_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to delete the records
        update_query = f"""
            DELETE FROM user_cluster_{user_id}
            WHERE file_id = %s;
        """

        # execute the delete query
        cursor.execute(update_query, (file_id,))

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
    

def delete_file_from_cluster(user_id, file_id, cluster_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to delete the records
        update_query = f"""
            DELETE FROM user_cluster_{user_id}
            WHERE file_id = %s AND cluster_id = %s;
        """

        # execute the delete query
        cursor.execute(update_query, (file_id, cluster_id))

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
