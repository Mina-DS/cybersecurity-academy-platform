import os
import secrets
from PIL import Image
from Python_Project import app, bcrypt, db, mail
from flask_mail import Message
from flask import render_template, url_for, flash, redirect, request
from .forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm
from .models import User, Course
from flask_login import login_user, current_user, logout_user, login_required

Courses = [
    {
        'name': 'Web Penetration Testing',
        'icon': 'web.webp'
    },
    {
        'name': 'Android Penetration Testing',
        'icon': 'Android.jpg'
    },
    {
        'name': 'Network Penetration Testing',
        'icon': 'Network.jpg'
    },
    {
        'name': 'Active Directory Penetration Testing',
        'icon': 'AD.jpg'
    },
    {
        'name': 'API Penetration Testing',
        'icon': 'API.jpg'
    },
    {
        'name': 'Cloud Penetration Testing',
        'icon': 'Cloud.png'
    }
]

def save_picture(form_picture):
    radnom_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = radnom_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/user_pics', picture_name)
    output_size = (160, 160)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_name

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', Courses=Courses)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/warning.html')
def warning():
    return render_template('warning.html')


@app.route('/register', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(fname=form.fname.data, lname=form.lname.data, username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created successfully for {form.username.data}", 'success')
        return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request",
        sender="testbugs028@gmail.com",
        recipients=[user.email],
        body=f'''Visit the following link to reset your password:
        {url_for('reset_password', token=token, _external=True)}

        if you did not request a password reset, please ignore this email.'''
    )
    mail.send(msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f"Welcome, {user.fname}!", "success")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Invalid email/password", "danger")

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    profile_form = UpdateProfileForm()
    if profile_form.validate_on_submit():
        if profile_form.picture.data:
            picture_file = save_picture(profile_form.picture.data)
            current_user.image_file = picture_file
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.bio = profile_form.bio.data
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('dashboard'))
    elif request.method == "GET":
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email
        profile_form.bio.data = current_user.bio

    image_file = url_for('static', filename=f'user_pics/{current_user.image_file}')
    return render_template('dashboard.html', title='Dashboard', profile_form=profile_form, image_file=image_file)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('If this account exists, check your email for the reset password link', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('The token is invalid or expired', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated successfully. You can now login with the new password.", "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', form=form)