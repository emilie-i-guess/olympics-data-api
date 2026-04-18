import pandas as pd
import os
from app import models


def seed_data(db):
    print("Reading CSV file... This may take a little while...")

    # Finding correct path to file
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "athlete_events.csv")

    df = pd.read_csv("athlete_events.csv").head(20000)
    df = df.where(pd.notnull(df), None)

    print(f"Starting import of {len(df)} rows...")

    for index, row in df.iterrows():
        # Creating an object based on model in models.py
        new_row = models.OlympicResult(
            athlete_id=row["ID"],
            name=row["Name"],
            sex=row["Sex"],
            age=row["Age"],
            height=row["Height"],
            weight=row["Weight"],
            team=row["Team"],
            noc=row["NOC"],
            games=row["Games"],
            year=row["Year"],
            season=row["Season"],
            city=row["City"],
            sport=row["Sport"],
            event=row["Event"],
            medal=row["Medal"],
        )
        db.add(new_row)

        if index % 1000 == 0:
            db.commit()
            print(f"Saved {index} rows...")

    db.commit()
    print("Database has been successfully filled with OL data.")

