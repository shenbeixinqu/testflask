
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response
from flask_login import current_user
from bluelog.forms import SuggesstionForm


from bluelog.extensions import db
from bluelog.models import Post, Category,Moban
from bluelog.utils import redirect_back

# current_app.config["CKEDITOR_PKG_TYPE"]="full"

blog_bp = Blueprint('blog', __name__)

# 主页
@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.filter_by(reviewed=True).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)


# 分类展示
@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)



# 文章展示
@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):

    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.filter_by(reviewed=True).order_by(Post.timestamp.asc()).paginate(
        page, per_page)
    posts = pagination.items
    # form = SuggesstionForm()
    if request.method == "POST":
       sugg = {"Y": True, "N": False}
       sugges = request.values.get("sugges")
       though = request.values.get("though")
       # post.reviewed = sugg[through]
       post.reviewed = sugg[though]
       post.suggestion = sugges
       db.session.commit()
       return redirect(url_for('admin.manage_post', filter="unread"))

       # if form.validate_on_submit():
    #     # sugg = {"是":True,"否":False}
    #     # through = form.through.data
    #     # post.reviewed = sugges[sugg]
    #     through = form.through.data
    #     recomment = form.recomment.data
    #     post.suggestion=recomment
    #     post.reviewed = through
    #     db.session.commit()

        # return redirect(url_for('admin.manage_post',filter="unread"))


    return render_template('blog/post.html', posts=posts, pagination=pagination,post=post)



# 改变主题
@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
    return response


