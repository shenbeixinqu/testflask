import os

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail

from bluelog.extensions import db
from bluelog.forms import PostForm, CategoryForm,MobanForm
from bluelog.models import Post, Category,Admin,Moban
from bluelog.utils import redirect_back, allowed_file

from sqlalchemy import not_,and_

from bluelog.wechat import Wechat



admin_bp = Blueprint('admin', __name__)



# 管理文章
@admin_bp.route('/post/manage')
@login_required
def manage_post():
    # page = request.args.get('page', 1, type=int)
    # pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
    #     page, per_page=current_app.config['BLUELOG_MANAGE_POST_PER_PAGE'])
    # posts = pagination.items
    # return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = current_app.config['BLUELOG_POST_PER_PAGE'] # 每页数量
    if filter_rule == 'unread':
        filtered_posts = Post.query.filter(and_(Post.reviewed == False, Post.suggestion == None))
    elif filter_rule == "read":
        filtered_posts = Post.query.filter_by(reviewed=True)
    else:
        filtered_posts = Post.query.filter(and_(Post.reviewed == False,Post.suggestion.isnot(None)))

    # 分页对象
    pagination = filtered_posts.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    # 当前页数的记录列表
    posts = pagination.items
    return render_template('admin/manage_post.html', posts=posts,page=page, pagination=pagination)

# 管理成员
@admin_bp.route('/member/manage/')
@login_required
def manage_member():
    page = request.args.get('page', 1, type=int)
    pagination = Admin.query.order_by('username').paginate(
        page, per_page=current_app.config['BLUELOG_MANAGE_POST_PER_PAGE'])
    members = pagination.items
    return render_template('admin/manage_member.html', page=page, pagination=pagination,members=members)

# 通过管理员
@admin_bp.route('/member/<int:member_id>/approve',methods=["POST"])
@login_required
def approve_member(member_id):
    member = Admin.query.get_or_404(member_id)
    member.is_admin = True
    db.session.commit()
    flash("通过成功","success")
    return redirect_back()

# 通过文章
@admin_bp.route('/post/<int:post_id>/approve', methods=['POST'])
@login_required
def approve_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.reviewed = True
    db.session.commit()
    flash('通过成功', 'success')
    return redirect(url_for('admin.manage_post',filter="unread"))

# 文章不能通过
@admin_bp.route('post/<int:post_id>/unapprove',methods=["POST"])
@login_required
def unapprove_post(post_id):
    post = Post.query.get_or_404(post_id)
    suggestion = request.form.get('username')
    post.suggestion = suggestion
    db.session.commit()
    flash("文章未通过","success")
    return redirect(url_for('admin.manage_post',filter="unread"))
    # return redirect_back()



# 新文章
@admin_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    mobans = Moban.query.all()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        obperson = form.obperson.data
        category = Category.query.get(form.category.data)
        author = current_user.username
        post = Post(title=title, body=body, category=category,obperson=obperson,author=author)
        send_post = Post.query.filter_by(reviewed=False).count()
        send_post = send_post + 12
        db.session.add(post)
        db.session.commit()
        if current_user.is_admin:
            flash('添加成功', 'success')
            return redirect(url_for('blog.show_post', post_id=post.id))
        else:
            flash('您的文章正在审核', 'info')
            msg = '有新的文章请您审核\n' \
                  'http://172.18.5.118:5000/post/{0}'.format(send_post)
            wechat = Wechat()
            wechat.Send_Message(msg)
            return redirect(url_for('blog.index'))
    return render_template('admin/new_post.html', form=form,mobans=mobans)

# 添加模板
@admin_bp.route('/moban/new',methods=['GET','POST'])
def new_moban():
    form = MobanForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        moban = Moban(title=title,body=body)
        db.session.add(moban)
        db.session.commit()
        flash("添加成功","success")
        return redirect(url_for('admin.new_post'))
    return render_template('admin/new_moban.html', form=form)


# 编辑模板
@admin_bp.route('/post/new/moban/<int:moban_id>',methods=['GET','POST'])
@login_required
def edit_moban(moban_id):
    form = PostForm()
    mobans = Moban.query.all()
    moban = Moban.query.get_or_404(moban_id)
    if form.validate_on_submit():
        # moban = Moban.query.get_or_404(moban_id)
        body = form.body.data
        title = form.title.data
        obperson = form.obperson.data
        category = Category.query.get(form.category.data)
        author = current_user.username
        post = Post(title=title, body=body, category=category, obperson=obperson, author=author)
        send_post = Post.query.filter_by(reviewed=False).order_by(Post.timestamp.desc()).count() + 2
        print(send_post)
        db.session.add(post)
        db.session.commit()
        if current_user.is_admin:
            flash('添加成功', 'success')
            return redirect(url_for('blog.show_post', post_id=post.id))
        else:
            flash('您的文章正在审核', 'info')
            url = 'http://172.18.5.118:5000/post/{0}'.format(send_post)
            msg = '有新的文章请您审核\n' + url
                  # 'http://172.18.5.118:5000/post/{0}'.format(send_post)
            if url:
                return redirect(url_for('auth.login',username="admin",password="helloflask"))
            wechat = Wechat()
            wechat.Send_Message(msg)
            return redirect(url_for('blog.index'))
    form.body.data = moban.body
    return render_template('admin/new_post.html', form=form,mobans=mobans)

# 管理模板
@admin_bp.route('/moban/manage/')
@login_required
def manage_moban():
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']  # 每页数量
    pagination = Moban.query.paginate(page, per_page=per_page)

    # 当前页数的记录列表
    mobans = pagination.items
    return render_template('admin/manage_moban.html', mobans=mobans, page=page, pagination=pagination)

    # pagination = Admin.query.order_by('username').paginate(
    #     page, per_page=current_app.config['BLUELOG_MANAGE_POST_PER_PAGE'])
    # members = pagination.items
    # return render_template('admin/manage_member.html', page=page, pagination=pagination,members=members)

# 修改模板
@admin_bp.route('/moban/<int:moban_id>/modify', methods=['GET', 'POST'])
@login_required
def modify_moban(moban_id):
    form = MobanForm()
    moban = Moban.query.get_or_404(moban_id)
    if form.validate_on_submit():
        moban.title = form.title.data
        moban.body = form.body.data
        db.session.commit()
        flash('修改成功', 'success')
        return redirect(url_for('admin.manage_moban'))
    form.title.data = moban.title
    form.body.data = moban.body
    return render_template('admin/edit_moban.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('更新成功', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('删除成功', 'success')
    return redirect_back()


@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('禁止评论', 'success')
    else:
        post.can_comment = True
        flash('允许评论', 'success')
    db.session.commit()
    return redirect_back()






@admin_bp.route('/category/manage')
@login_required
def manage_category():
    # page = request.args.get('page', 1, type=int)
    # pagination = Category.query.order_by(Category.status).paginate(
    #     page, per_page=current_app.config['BLUELOG_MANAGE_POST_PER_PAGE'])
    # categorys = pagination.items
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']  # 每页数量

    # 分页对象
    pagination = Category.query.order_by(Category.status).paginate(page, per_page=per_page)
    # 当前页数的记录列表
    categories = pagination.items
    return render_template('admin/manage_category.html',categories=categories,page=page,pagination=pagination)


@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data

        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('创建分类成功', 'success')
        return redirect(url_for('.manage_category'))
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('你不能编辑分类', 'warning')
        return redirect(url_for('blog.index'))
    if form.validate_on_submit():
        # category.status = form.status.data
        category.name = form.name.data
        db.session.commit()
        flash('分类更新成功', 'success')
        return redirect(url_for('.manage_category'))

    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('你不能删除该分类', 'warning')
        return redirect(url_for('blog.index'))
    if category.status == "使用中":
        category.status = "废弃"
        db.session.commit()
    # category.delete()
        flash('分类废弃成功', 'success')
        return redirect(url_for('.manage_category'))
    else:
        category.status = "使用中"
        db.session.commit()
        # category.delete()
        flash('分类启用成功', 'success')
        return redirect(url_for('.manage_category'))


@admin_bp.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['BLUELOG_UPLOAD_PATH'], filename)


@admin_bp.route('/upload', methods=['POST'])
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('Image only!')
    f.save(os.path.join(current_app.config['BLUELOG_UPLOAD_PATH'], f.filename))
    url = url_for('.get_image', filename=f.filename)
    return upload_success(url, f.filename)


