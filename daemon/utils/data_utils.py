def parse_db_data_to_json(db_data):
    json_data = {}
    for rows in db_data:
        cluster_id = rows[1]
        file_id = rows[2]
        x1, y1, x2, y2 = rows[3], rows[4], rows[5], rows[6]

        if cluster_id in json_data:
            json_data[cluster_id].append({
                "file_id": file_id,
                "coords": [x1, y1, x2, y2]
            })
        else:
            json_data[cluster_id] = [{
                "file_id": file_id,
                "coords": [x1, y1, x2, y2]
            }]

    return json_data
