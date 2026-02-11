"""
Seed data for NCERT subjects and topics
"""

from sqlalchemy.orm import Session
from app.models import Subject, Topic
import uuid


# NCERT subjects by grade
SUBJECTS_DATA = [
    # Grade 3
    {"name": "Mathematics", "grade": 3, "description": "NCERT Mathematics for Grade 3", "icon": "calculator"},
    {"name": "English", "grade": 3, "description": "NCERT English for Grade 3", "icon": "book"},
    {"name": "Hindi", "grade": 3, "description": "NCERT Hindi for Grade 3", "icon": "language"},
    {"name": "Environmental Studies", "grade": 3, "description": "NCERT EVS for Grade 3", "icon": "leaf"},

    # Grade 4
    {"name": "Mathematics", "grade": 4, "description": "NCERT Mathematics for Grade 4", "icon": "calculator"},
    {"name": "English", "grade": 4, "description": "NCERT English for Grade 4", "icon": "book"},
    {"name": "Hindi", "grade": 4, "description": "NCERT Hindi for Grade 4", "icon": "language"},
    {"name": "Environmental Studies", "grade": 4, "description": "NCERT EVS for Grade 4", "icon": "leaf"},

    # Grade 5
    {"name": "Mathematics", "grade": 5, "description": "NCERT Mathematics for Grade 5", "icon": "calculator"},
    {"name": "English", "grade": 5, "description": "NCERT English for Grade 5", "icon": "book"},
    {"name": "Hindi", "grade": 5, "description": "NCERT Hindi for Grade 5", "icon": "language"},
    {"name": "Environmental Studies", "grade": 5, "description": "NCERT EVS for Grade 5", "icon": "leaf"},

    # Grade 6
    {"name": "Mathematics", "grade": 6, "description": "NCERT Mathematics for Grade 6", "icon": "calculator"},
    {"name": "Science", "grade": 6, "description": "NCERT Science for Grade 6", "icon": "flask"},
    {"name": "Social Science", "grade": 6, "description": "NCERT Social Science for Grade 6", "icon": "globe"},
    {"name": "English", "grade": 6, "description": "NCERT English for Grade 6", "icon": "book"},
    {"name": "Hindi", "grade": 6, "description": "NCERT Hindi for Grade 6", "icon": "language"},

    # Grade 7
    {"name": "Mathematics", "grade": 7, "description": "NCERT Mathematics for Grade 7", "icon": "calculator"},
    {"name": "Science", "grade": 7, "description": "NCERT Science for Grade 7", "icon": "flask"},
    {"name": "Social Science", "grade": 7, "description": "NCERT Social Science for Grade 7", "icon": "globe"},
    {"name": "English", "grade": 7, "description": "NCERT English for Grade 7", "icon": "book"},
    {"name": "Hindi", "grade": 7, "description": "NCERT Hindi for Grade 7", "icon": "language"},

    # Grade 8
    {"name": "Mathematics", "grade": 8, "description": "NCERT Mathematics for Grade 8", "icon": "calculator"},
    {"name": "Science", "grade": 8, "description": "NCERT Science for Grade 8", "icon": "flask"},
    {"name": "Social Science", "grade": 8, "description": "NCERT Social Science for Grade 8", "icon": "globe"},
    {"name": "English", "grade": 8, "description": "NCERT English for Grade 8", "icon": "book"},
    {"name": "Hindi", "grade": 8, "description": "NCERT Hindi for Grade 8", "icon": "language"},

    # Grade 9
    {"name": "Mathematics", "grade": 9, "description": "NCERT Mathematics for Grade 9", "icon": "calculator"},
    {"name": "Science", "grade": 9, "description": "NCERT Science for Grade 9", "icon": "flask"},
    {"name": "Social Science", "grade": 9, "description": "NCERT Social Science for Grade 9", "icon": "globe"},
    {"name": "English", "grade": 9, "description": "NCERT English for Grade 9", "icon": "book"},
    {"name": "Hindi", "grade": 9, "description": "NCERT Hindi for Grade 9", "icon": "language"},

    # Grade 10
    {"name": "Mathematics", "grade": 10, "description": "NCERT Mathematics for Grade 10", "icon": "calculator"},
    {"name": "Science", "grade": 10, "description": "NCERT Science for Grade 10", "icon": "flask"},
    {"name": "Social Science", "grade": 10, "description": "NCERT Social Science for Grade 10", "icon": "globe"},
    {"name": "English", "grade": 10, "description": "NCERT English for Grade 10", "icon": "book"},
    {"name": "Hindi", "grade": 10, "description": "NCERT Hindi for Grade 10", "icon": "language"},
]


# Sample topics for Grade 5 Mathematics (can be expanded later)
TOPICS_DATA = {
    "Mathematics_5": [
        {"name": "Patterns", "description": "Understanding patterns and sequences", "order": 1},
        {"name": "Numbers", "description": "Large numbers and place value", "order": 2},
        {"name": "Addition and Subtraction", "description": "Addition and subtraction of large numbers", "order": 3},
        {"name": "Multiplication", "description": "Multiplication methods", "order": 4},
        {"name": "Division", "description": "Division of numbers", "order": 5},
        {"name": "Fractions", "description": "Understanding fractions", "order": 6},
        {"name": "Decimals", "description": "Introduction to decimals", "order": 7},
        {"name": "Shapes and Angles", "description": "Basic geometry", "order": 8},
        {"name": "Area and Perimeter", "description": "Calculating area and perimeter", "order": 9},
        {"name": "Data Handling", "description": "Basic statistics", "order": 10},
    ],
    "Science_6": [
        {"name": "Food: Where Does it Come From?", "description": "Sources of food", "order": 1},
        {"name": "Components of Food", "description": "Nutrients in food", "order": 2},
        {"name": "Fibre to Fabric", "description": "Making of fabrics", "order": 3},
        {"name": "Sorting Materials into Groups", "description": "Properties of materials", "order": 4},
        {"name": "Separation of Substances", "description": "Methods of separation", "order": 5},
        {"name": "Changes Around Us", "description": "Physical and chemical changes", "order": 6},
        {"name": "Living Organisms and Their Surroundings", "description": "Habitats and adaptation", "order": 7},
        {"name": "Motion and Measurement of Distances", "description": "Understanding motion", "order": 8},
        {"name": "Light, Shadows and Reflections", "description": "Properties of light", "order": 9},
        {"name": "Electricity and Circuits", "description": "Basic electrical circuits", "order": 10},
    ],
}


def seed_subjects(db: Session) -> dict:
    """Seed subjects into database"""
    subject_map = {}

    for subject_data in SUBJECTS_DATA:
        # Check if subject already exists
        existing = db.query(Subject).filter_by(
            name=subject_data["name"],
            grade=subject_data["grade"]
        ).first()

        if not existing:
            subject = Subject(
                id=str(uuid.uuid4()),
                **subject_data
            )
            db.add(subject)
            db.flush()
            subject_map[f"{subject_data['name']}_{subject_data['grade']}"] = subject.id
        else:
            subject_map[f"{subject_data['name']}_{subject_data['grade']}"] = existing.id

    db.commit()
    return subject_map


def seed_topics(db: Session, subject_map: dict) -> None:
    """Seed topics into database"""

    for subject_key, topics in TOPICS_DATA.items():
        subject_id = subject_map.get(subject_key)

        if not subject_id:
            print(f"Warning: Subject not found for {subject_key}")
            continue

        for topic_data in topics:
            # Check if topic already exists
            existing = db.query(Topic).filter_by(
                subject_id=subject_id,
                name=topic_data["name"]
            ).first()

            if not existing:
                topic = Topic(
                    id=str(uuid.uuid4()),
                    subject_id=subject_id,
                    **topic_data
                )
                db.add(topic)

    db.commit()


def seed_all(db: Session) -> None:
    """Seed all data"""
    print("Seeding subjects...")
    subject_map = seed_subjects(db)
    print(f"Created/verified {len(subject_map)} subjects")

    print("Seeding topics...")
    seed_topics(db, subject_map)
    print("Topics seeded successfully")

    print("Seed data complete!")


if __name__ == "__main__":
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()
