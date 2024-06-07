from . import connection


def create_user_cluster_table(user_id):
    try:
        # initialize cursor
        cursor = connection.cursor()

        # query to create a new table if not exists in MySQL database
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS user_cluster_{user_id} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cluster_id CHAR(36),
                file_id CHAR(36),
                x1 INT, y1 INT, x2 INT,  y2 INT,
                matched_score INT,
                cluster_name VARCHAR(30),
                is_identity BOOLEAN
            );
        """

        # Execute the creation table query
        cursor.execute(create_table_query)

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


def get_user_cluster_info(user_id):
    try:
        # initialize cursor
        cursor = connection.cursor()

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


def insert_user_cluster_record(user_id, cluster_id, file_id, coords, matched_score, cluster_name=None, is_identity=False):
    try:
        # initialize cursor
        cursor = connection.cursor()

        # query to insert the record in MySQL database
        insert_query = f"""
            INSERT INTO user_cluster_{user_id} (cluster_id, file_id, x1, y1, x2, y2, matched_score, cluster_name, is_identity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        x1, y1, x2, y2 = coords
        # Execute the insert table query
        cursor.execute(insert_query, (cluster_id, file_id, x1, y1, x2, y2, matched_score, cluster_name, is_identity))

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
