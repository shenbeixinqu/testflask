
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from bluelog.extensions import db




# 用户
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    is_admin = db.Column(db.Boolean, default=False)

    posts = db.relationship('Post', back_populates='admin')

    # role_id = db.Column(db.Integer)


    # blog_title = db.Column(db.String(60))
    # blog_sub_title = db.Column(db.String(100))
    # name = db.Column(db.String(30))
    # about = db.Column(db.Text)



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

# # 权限
# class Permissions:
#     USER_MANAGE = 0X01
#     UPDATE_PERMISSION = 0x02


# 文章
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    obperson = db.Column(db.Integer)
    author = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # can_comment = db.Column(db.Boolean, default=True)
    reviewed = db.Column(db.Boolean, default=False)
    suggestion= db.Column(db.Text,default=None)


    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    admin = db.relationship('Admin', back_populates='posts')
    category = db.relationship('Category', back_populates='posts')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    status = db.Column(db.Enum(
         '使用中', '废弃'
    ), server_default='使用中', nullable=False)

    posts = db.relationship('Post', back_populates='category')

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()

# 模板

class Moban(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)


