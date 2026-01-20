from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Ensure app imports work when running as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import AppConfig  # noqa: E402
from app.models import Base  # noqa: E402
from scripts.seed_data import run_seed  # noqa: E402


def main() -> None:
    config = AppConfig()
    engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            run_seed(session, config)
            session.commit()
    except IntegrityError:
        print("Seed already applied or constraint violated")


if __name__ == "__main__":
    main()
