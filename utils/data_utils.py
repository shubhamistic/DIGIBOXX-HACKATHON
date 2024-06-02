def parse_db_data_to_json(db_data):
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
