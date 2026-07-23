import os
from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, Report, User  # Added User model
from forms import ReportProblemForm, AskForm, RegistrationForm, LoginForm  # Added Auth forms
from groq import Groq
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tbilisi_clean_secret_key_2026'

# Configure Database
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'tbilisi.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'  # Redirects users to /login if a page requires being logged in
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


client = Groq(api_key="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")

with app.app_context():
    db.create_all()
    # Let's auto-create an Admin user so you can test Admin exclusive functions easily!
    admin_exists = User.query.filter_by(email="admin@aat.ge").first()
    if not admin_exists:
        hashed_pw = generate_password_hash("admin123", method='pbkdf2:sha256')
        admin_user = User(username="Admin", email="admin@aat.ge", password=hashed_pw, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()


# --- ALL ROUTE DEFINITIONS ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/air-quality')
def air_quality():
    return render_template('air_quality.html')


@app.route('/educational')
def educational():
    return render_template('educational.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


# --- USER AUTHENTICATION ROUTES ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        user_exists = User.query.filter_by(email=form.email.data).first()
        if user_exists:
            return render_template('signup.html', form=form, error="Email already registered.")

        # Securely hash password and save user
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', form=form, error="Invalid email or password.")

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/ask', methods=['GET', 'POST'])
def ai_page():
    form = AskForm()
    answer = None
    if form.validate_on_submit():
        question = form.question.data
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful eco-assistant for the ECO TBILISI platform. Answer questions about recycling, ecology, and saving the environment in Tbilisi, Georgia."
                    },
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=600  # Prevents long generation hangs
            )
            answer = chat_completion.choices[0].message.content
        except Exception as e:
            # This will print the exact issue to your PyCharm console for debugging
            print(f"Groq API Error: {str(e)}")
            answer = f"Technical difficulties: Could not reach the AI assistant. (Details: {str(e)})"

    return render_template('ask_ai.html', form=form, answer=answer)


#
@app.route('/report', methods=['GET', 'POST'])
def report():
    form = ReportProblemForm()
    if form.validate_on_submit():
        new_report = Report(
            location=form.location.data,
            description=form.description.data
        )
        db.session.add(new_report)
        db.session.commit()
        return redirect(url_for('report'))

    all_reports = Report.query.all()
    return render_template('report.html', form=form, reports=all_reports)


# Exclusive Admin Route
@app.route('/report/delete/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    if not current_user.is_admin:
        return "Access Denied: Admins only.", 403

    report_to_delete = Report.query.get_or_be_404(report_id)
    db.session.delete(report_to_delete)
    db.session.commit()
    return redirect(url_for('report'))


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=true)
