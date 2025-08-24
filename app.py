from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_bcrypt import Bcrypt
from datetime import datetime, date, time
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# -----------------------
# Models
# -----------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship("Appointment", backref="user", lazy=True)
    prescriptions = db.relationship("Prescription", backref="user", lazy=True)
    records = db.relationship("MedicalRecord", backref="user", lazy=True)
    invoices = db.relationship("Invoice", backref="user", lazy=True)

    def set_password(self, pw):
        self.password_hash = bcrypt.generate_password_hash(pw).decode("utf-8")

    def check_password(self, pw):
        return bcrypt.check_password_hash(self.password_hash, pw)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    hospital = db.Column(db.String(160), nullable=False)
    contact = db.Column(db.String(120), nullable=False)
    work_hours = db.Column(db.String(160), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float, default=4.6)

    appointments = db.relationship("Appointment", backref="doctor_obj", lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.String(255))

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    notes = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor_name = db.Column(db.String(120), nullable=False)
    medication = db.Column(db.String(160), nullable=False)
    dosage = db.Column(db.String(120), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    issued_on = db.Column(db.Date, default=date.today)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    item = db.Column(db.String(160), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Unpaid")
    issued_on = db.Column(db.Date, default=date.today)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------
# Forms
# -----------------------
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")

class AppointmentForm(FlaskForm):
    doctor_id = SelectField("Doctor", coerce=int, validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])
    time = TimeField("Time", validators=[DataRequired()])
    reason = StringField("Reason", validators=[Length(max=255)])
    submit = SubmitField("Book Appointment")

# -----------------------
# Routes
# -----------------------
@app.route("/", methods=["GET", "POST"])
def login():
    # Home = login, as requested
    form = LoginForm()
    reg = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid email or password", "danger")
    return render_template("login_home.html", form=form, reg=reg)

@app.route("/register", methods=["POST"])
def register():
    reg = RegisterForm()
    if reg.validate_on_submit():
        if User.query.filter_by(email=reg.email.data.lower()).first():
            flash("Email already registered", "warning")
            return redirect(url_for("login"))
        u = User(full_name=reg.full_name.data, email=reg.email.data.lower())
        u.set_password(reg.password.data)
        db.session.add(u)
        db.session.commit()
        flash("Account created! Please log in.", "success")
    else:
        flash("Please correct the errors and try again.", "danger")
    return redirect(url_for("login"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    doctors = Doctor.query.limit(6).all()
    next_appt = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.date, Appointment.time).first()
    return render_template("dashboard.html", doctors=doctors, next_appt=next_appt)

@app.route("/doctors")
@login_required
def doctors():
    q = request.args.get("q","").strip()
    spec = request.args.get("spec","").strip()
    query = Doctor.query
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(db.or_(db.func.lower(Doctor.name).like(like), db.func.lower(Doctor.hospital).like(like)))
    if spec:
        query = query.filter(Doctor.specialization==spec)
    specs = [s[0] for s in db.session.query(Doctor.specialization).distinct().all()]
    return render_template("doctors.html", doctors=query.all(), specs=specs, q=q, spec=spec)

@app.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    form = AppointmentForm()
    form.doctor_id.choices = [(d.id, f"{d.name} — {d.specialization}") for d in Doctor.query.all()]
    if form.validate_on_submit():
        a = Appointment(user_id=current_user.id, doctor_id=form.doctor_id.data, date=form.date.data, time=form.time.data, reason=form.reason.data)
        db.session.add(a)
        db.session.commit()
        flash("Appointment booked!", "success")
        return redirect(url_for("appointments"))
    appts = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return render_template("appointments.html", form=form, appts=appts)

@app.route("/services")
@login_required
def services():
    return render_template("services.html", services=Service.query.all())

@app.route("/records")
@login_required
def records():
    return render_template("records.html", records=MedicalRecord.query.filter_by(user_id=current_user.id).all())

@app.route("/prescriptions")
@login_required
def prescriptions():
    return render_template("prescriptions.html", items=Prescription.query.filter_by(user_id=current_user.id).all())

@app.route("/billing")
@login_required
def billing():
    return render_template("billing.html", invoices=Invoice.query.filter_by(user_id=current_user.id).all())

# API to expose doctor meta (optional for SPA hooks)
@app.route("/api/doctors")
@login_required
def api_doctors():
    return jsonify([{
        "id": d.id, "name": d.name, "specialization": d.specialization, "hospital": d.hospital,
        "contact": d.contact, "work_hours": d.work_hours, "bio": d.bio, "photo": d.photo, "rating": d.rating
    } for d in Doctor.query.all()])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
