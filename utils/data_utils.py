def parse_user_data_to_json(db_data):
    json_data = []
    cur_data = {}  # temp variable
    for record in db_data:
        date = record[2]
        month_year = f"{date.month}/{date.year}"
        if cur_data in json_data and cur_data["date"] == month_year:
            cur_data = {
                "date": month_year,
                "info": json_data[-1]["info"] + [{
                    "fileId": record[0],
                    "fileType": record[1],
                    "uploadDate": f"{date.day}/{month_year}"
                }]
            }
            json_data[-1] = cur_data
        else:
            cur_data = {
                "date": month_year,
                "info": [{
                    "fileId": record[0],
                    "fileType": record[1],
                    "uploadDate": f"{date.day}/{month_year}"
                }]
            }
            json_data.append(cur_data)

    return json_data


def parse_user_cluster_data_to_json(db_cluster):
    json_data = {}
    for rows in db_cluster:
        cluster_id = rows[1]
        file_id = rows[2]
        x1, y1, x2, y2 = rows[3], rows[4], rows[5], rows[6]
        matched_score = rows[7]
        cluster_name = rows[8]

        if "clusterId" in json_data:
            json_data["data"].append({
                "file_id": file_id,
                "coords": [x1, y1, x2, y2],
                "matchedScore": matched_score
            })
        else:
            json_data["clusterId"] = cluster_id
            json_data["clusterName"] = cluster_name
            json_data["data"] = [{
                "file_id": file_id,
                "coords": [x1, y1, x2, y2],
                "matchedScore": matched_score
            }]

    return json_data


def parse_user_distinct_cluster_to_json(db_data):
    json_data = []
    for rows in db_data:
        cluster_id = rows[1]
        file_id = rows[2]
        x1, y1, x2, y2 = rows[3], rows[4], rows[5], rows[6]
        cluster_name = rows[8]

        json_data.append({
            "clusterId": cluster_id,
            "clusterName": cluster_name,
            "fileId": file_id,
            "coords": [x1, y1, x2, y2]
        })

    return json_data


def parse_user_cluster_data_to_json_for_clustering(db_data):
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
