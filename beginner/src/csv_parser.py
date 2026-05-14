import csv
from .model import TeamSchema
from pydantic import ValidationError

# def parse_with_builtin():
#     with open("male_teams.csv", newline="", encoding="utf-8") as f:
#         reader = csv.DictReader(f)

#         for row in reader:
#             print(row)  

def get_csv_reader(file_path):
    f = open(file_path, mode='r', encoding='utf-8', newline='')
    return csv.DictReader(f), f

def validate_csv(file_path):
    valid_data = []
    errors = []

    reader, file_handle = get_csv_reader(file_path)
    try:
        for row in reader:
            try:
                team = TeamSchema(**row)
                valid_data.append(team)
            except ValidationError as e:
                errors.append({"data": row, "error": e.json()})
    finally:
        file_handle.close()

    return valid_data, errors