import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import Wine
from app.payments import Subscription, PaymentMethod, Invoice, UsageAlert
from app.models import (
    User,
    APIKey,
    UsageLog,
    Webhook,
    WebhookDelivery,
    Team,
    TeamMember,
    WhiteLabelConfig,
)


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
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS webhook_deliveries CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS team_members CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS webhooks CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS api_keys CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS usage_logs CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS teams CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS white_label_configs CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS usage_alerts CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS invoices CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS payment_methods CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS subscriptions CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS wines CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.commit()
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
