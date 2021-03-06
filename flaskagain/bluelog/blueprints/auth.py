from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from bluelog.forms import LoginForm,RegisterForm
from bluelog.models import Admin
from bluelog.utils import redirect_back
from bluelog.extensions import db

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            if admin.validate_password(password):
                login_user(admin, remember)
                flash('欢迎回来', 'info')
                return redirect_back()
            flash('账号或密码错误', 'warning')
        else:
            flash('没有账户', 'warning')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = Admin(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('注册成功', 'info')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('退出成功', 'info')
    return redirect_back()
