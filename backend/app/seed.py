"""
Seeds the database with the bundled sample dataset (data/sample_sales.csv)
and creates a demo login account.

Run with:  python -m app.seed
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import Base, engine, SessionLocal
from app.models.models import User
from app.services import upload_service
from app.services.auth_service import hash_password

SAMPLE_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "data", "sample_sales.csv")


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not os.path.exists(SAMPLE_CSV):
            print(f"Sample CSV not found at {SAMPLE_CSV}. Skipping data seed.")
        else:
            df = pd.read_csv(SAMPLE_CSV)
            df["order_date"] = pd.to_datetime(df["order_date"])
            cleaned = upload_service.clean(df)
            rows = upload_service.ingest(db, cleaned)
            print(f"Seeded {rows:,} order line items from sample_sales.csv")

        demo_email = "demo@salesai.com"
        existing = db.query(User).filter(User.email == demo_email).first()
        if not existing:
            demo = User(name="Demo User", email=demo_email, password_hash=hash_password("Demo@1234"))
            db.add(demo)
            db.commit()
            print(f"Created demo account -> email: {demo_email} / password: Demo@1234")
        else:
            print("Demo account already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
