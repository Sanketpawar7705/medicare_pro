from app import app, db, User, Doctor, Service, MedicalRecord, Prescription, Invoice, Appointment
from datetime import date, time

with app.app_context():
    db.create_all()

    # Create demo user
    if not User.query.filter_by(email="demo@medicare.app").first():
        u = User(full_name="Demo User", email="demo@medicare.app")
        u.set_password("Demo@123")
        db.session.add(u)
        db.session.commit()

    # Doctors (10)
    if Doctor.query.count() == 0:
        doctors = [
    {
        "name": "Dr. Sarah Johnson",
        "specialization": "Cardiology",
        "hospital": "Nova Heart Institute",
        "contact": "+1 555-210-7788",
        "work_hours": "Mon, Wed, Fri — 9:00–17:00",
        "bio": "15+ years treating coronary artery disease and heart failure; preventive cardiology advocate.",
        "photo": "https://randomuser.me/api/portraits/women/44.jpg"
    },
    {
        "name": "Dr. Michael Chen",
        "specialization": "Neurology",
        "hospital": "Cerebra Neuro Center",
        "contact": "+1 555-889-2211",
        "work_hours": "Tue, Thu — 10:00–18:00",
        "bio": "Board-certified neurologist focused on migraines, epilepsy, and movement disorders.",
        "photo": "https://randomuser.me/api/portraits/men/32.jpg"
    },
    {
        "name": "Dr. Emily Williams",
        "specialization": "Pediatrics",
        "hospital": "Sunrise Children’s Hospital",
        "contact": "+1 555-661-0099",
        "work_hours": "Mon–Fri — 08:00–16:00",
        "bio": "Primary care for kids, adolescent medicine, and vaccination counseling.",
        "photo": "https://randomuser.me/api/portraits/women/68.jpg"
    },
    {
        "name": "Dr. Raj Patel",
        "specialization": "Orthopedics",
        "hospital": "Motion Ortho Clinic",
        "contact": "+1 555-774-9900",
        "work_hours": "Mon, Thu — 09:00–17:00",
        "bio": "Sports injuries, knee/hip replacements, and arthroscopy specialist.",
        "photo": "https://randomuser.me/api/portraits/men/56.jpg"
    },
    {
        "name": "Dr. Aisha Khan",
        "specialization": "Dermatology",
        "hospital": "Glow Skin Center",
        "contact": "+1 555-120-3344",
        "work_hours": "Tue–Sat — 11:00–19:00",
        "bio": "Acne, psoriasis, cosmetic dermatology, and dermoscopy.",
        "photo": "https://randomuser.me/api/portraits/women/12.jpg"
    },
    {
        "name": "Dr. Luis Garcia",
        "specialization": "Gastroenterology",
        "hospital": "Digestive Health Group",
        "contact": "+1 555-221-5566",
        "work_hours": "Mon–Fri — 09:30–17:30",
        "bio": "Endoscopy, IBS/IBD management, and hepatology.",
        "photo": "https://randomuser.me/api/portraits/men/71.jpg"
    },
    {
        "name": "Dr. Hana Suzuki",
        "specialization": "Endocrinology",
        "hospital": "Metabolic Care Center",
        "contact": "+1 555-998-2233",
        "work_hours": "Mon, Wed, Fri — 10:00–16:00",
        "bio": "Diabetes, thyroid disorders, and osteoporosis.",
        "photo": "https://randomuser.me/api/portraits/women/28.jpg"
    },
    {
        "name": "Dr. Omar Nasser",
        "specialization": "Pulmonology",
        "hospital": "Lung & Sleep Institute",
        "contact": "+1 555-552-7711",
        "work_hours": "Tue, Thu — 09:00–17:00",
        "bio": "Asthma, COPD, sleep apnea; certified in sleep medicine.",
        "photo": "https://randomuser.me/api/portraits/men/85.jpg"
    },
    {
        "name": "Dr. Sofia Rossi",
        "specialization": "Gynecology",
        "hospital": "Women’s Wellness Center",
        "contact": "+1 555-330-8899",
        "work_hours": "Mon–Fri — 10:00–18:00",
        "bio": "Preventive care, fertility counseling, and minimally invasive surgery.",
        "photo": "https://randomuser.me/api/portraits/women/45.jpg"
    }
]



        for d in doctors:
            db.session.add(Doctor(**d))
        db.session.commit()

    # Services
    if Service.query.count() == 0:
        services = [
            {"name": "General Consultation", "description": "Primary care visits for common ailments and referrals.", "price": 50},
            {"name": "Heart Check", "description": "ECG, lipid profile, and cardiologist review.", "price": 180},
            {"name": "Skin Screening", "description": "Full-body mole check and dermatology consult.", "price": 120},
            {"name": "Diabetes Package", "description": "HbA1c, endocrine consult, and diet plan.", "price": 140},
        ]
        for s in services:
            db.session.add(Service(**s))
        db.session.commit()

    # Sample data tied to demo user
    u = User.query.filter_by(email="demo@medicare.app").first()
    if u and MedicalRecord.query.filter_by(user_id=u.id).count() == 0:
        db.session.add(MedicalRecord(user_id=u.id, title="Annual Physical 2024",
                                     notes="Normal vitals, BMI 23.1, advised regular exercise."))
        db.session.add(MedicalRecord(user_id=u.id, title="Allergy Panel",
                                     notes="Mild pollen allergy; prescribed antihistamines as needed."))
        db.session.add(Prescription(user_id=u.id, doctor_name="Dr. Sarah Johnson", medication="Atorvastatin 10mg",
                                    dosage="1 tab daily", instructions="Take at night."))
        db.session.add(Invoice(user_id=u.id, item="General Consultation", amount=50, status="Paid"))

        # Upcoming appointment
        d1 = Doctor.query.filter_by(name="Dr. Sarah Johnson").first()
        if d1:
            db.session.add(Appointment(user_id=u.id, doctor_id=d1.id, date=date.today(), time=time(15, 0),
                                       reason="Follow-up"))

        db.session.commit()

    print("Seed complete.")


#.venv\Scripts\Activate.ps1
#flask --app app run --debug
