from beginner.src.csv_parser import validate_csv

def main():
    teams, errors = validate_csv(r'data/male_teams.csv')

    print(f"Successfully parsed {len(teams)} teams.")
    if errors:
        print(f"Found {len(errors)} validation issues.")

if __name__ == "__main__":
    main()