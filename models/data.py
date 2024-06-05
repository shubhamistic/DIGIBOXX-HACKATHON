from . import get_db


def create_user_data_table(user_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # query to create a new table if not exists in MySQL database
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS user_data_{user_id} (
                file_id CHAR(36) PRIMARY KEY,
                file_type CHAR(5),
                upload_date DATE
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


def insert_file_record(user_id, file_id, file_type):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to insert data with current date
        insert_query = f"""
            INSERT INTO user_data_{user_id} (file_id, file_type, upload_date)
            VALUES (%s, %s, CURRENT_DATE())
        """

        # Execute the insert record query
        cursor.execute(insert_query, (file_id, file_type))

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


def delete_file_record(user_id, file_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to delete data with the help of file_id key
        delete_query = f"""
            DELETE FROM user_data_{user_id}
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


def get_file_record(user_id, file_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to get the data with the help of file_id key
        select_query = f"""
            SELECT file_type FROM user_data_{user_id}
            WHERE file_id = %s;
        """

        # Execute the get record query
        cursor.execute(select_query, (file_id,))

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


def get_all_records_datewise_sorted(user_id):
    try:
        # initialize cursor
        db = get_db()
        cursor = db.connection.cursor()

        # SQL query to get the records sorted datewise from latest to oldest
        select_query = f"""
            SELECT * FROM user_data_{user_id}
            ORDER BY upload_date DESC;
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
