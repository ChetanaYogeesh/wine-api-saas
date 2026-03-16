import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import Wine


def init_db():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done!")


def import_wines(csv_path: str = "wine-ratings.csv"):
    """Import wines from CSV to database"""
    print(f"Importing wines from {csv_path}...")

    df = pd.read_csv(csv_path, index_col=0)
    df = df.drop(columns=["grape"], errors="ignore")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    db = SessionLocal()

    try:
        wines = []
        for idx, row in df.iterrows():
            wine = Wine(
                id=int(idx),
                name=row["name"],
                region=row.get("region"),
                variety=row.get("variety"),
                rating=row.get("rating"),
                notes=row.get("notes"),
            )
            wines.append(wine)

            if len(wines) >= 1000:
                db.bulk_save_objects(wines)
                db.commit()
                print(f"Imported {idx + 1} wines...")
                wines = []

        if wines:
            db.bulk_save_objects(wines)
            db.commit()

        print(f"Successfully imported {len(df)} wines!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


def reset_db():
    """Drop all tables and recreate"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Done! Tables dropped.")
    init_db()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database migration script")
    parser.add_argument(
        "--init", action="store_true", help="Initialize database tables"
    )
    parser.add_argument(
        "--import",
        dest="import_wines",
        action="store_true",
        help="Import wines from CSV",
    )
    parser.add_argument(
        "--reset", action="store_true", help="Reset database (drop and recreate)"
    )
    parser.add_argument(
        "--csv-path", default="wine-ratings.csv", help="Path to CSV file"
    )

    args = parser.parse_args()

    if args.reset:
        reset_db()
    elif args.init:
        init_db()
    elif args.import_wines:
        import_wines(args.csv_path)
    else:
        print("Please specify --init, --import, or --reset")
        print("Examples:")
        print("  python -m app.migrate --init              # Create tables")
        print("  python -m app.migrate --import            # Import wines")
        print("  python -m app.migrate --reset              # Reset database")
