# users/views.py
from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from BloomBuddy import db
from BloomBuddy.models import User, BlogPost, Plant
from BloomBuddy.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from BloomBuddy.users.picture_handler import add_profile_pic
from werkzeug.security import generate_password_hash

users = Blueprint('users', __name__)


# register
@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registration!')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)


# login
@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.check_password(form.password.data) and user is not None:
            login_user(user)
            flash('Log in Success!')
            next = request.args.get('next')
            if next == None or not next[0] == '/':
                next = url_for('core.home')
            return redirect(next)
    return render_template('login.html', form=form)


# logout
@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("core.home"))


# account (update UserForm)
@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateUserForm()
    plants = Plant.query.filter_by(user_id=current_user.id).all()
    users = None
    if current_user.is_admin:
        users = User.query.order_by(User.username).all()
    if form.validate_on_submit():
        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data, username)
            current_user.profile_image = pic
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('User Account Updated')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('account.html', profile_image=profile_image, form=form, plants=plants, users=users)


@users.route("/<username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    blog_posts = BlogPost.query.filter_by(author=user) \
        .order_by(BlogPost.date.desc()) \
        .paginate(page=page, per_page=5)
    plants = Plant.query.filter_by(user_id=user.id).all()
    return render_template('user_blog_posts.html', blog_posts=blog_posts, user=user, plants=plants)


@users.route('/save_plants', methods=['POST'])
@login_required
def save_plants():
    data = request.get_json()
    for plant in data['plants']:
        new_plant = Plant(name=plant['name'], age=plant['age'], health=plant['health'], user_id=current_user.id)
        db.session.add(new_plant)
    db.session.commit()
    return jsonify({'message': 'Plants saved successfully'}), 200

@users.route('/delete_plant/<int:plant_id>', methods=['DELETE'])
@login_required
def delete_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    if plant.user_id != current_user.id:
        abort(403)
    db.session.delete(plant)
    db.session.commit()
    return jsonify({'message': 'Plant deleted successfully'}), 200

@users.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200