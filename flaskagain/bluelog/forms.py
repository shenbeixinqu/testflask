from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField,SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL,Regexp,EqualTo

from bluelog.models import Category,Admin


class LoginForm(FlaskForm):
    username = StringField('账号', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class SuggesstionForm(FlaskForm):
    # through = SelectField('是否通过', choices=[
    #     (1, '是'),
    #     (2, '否'),
    # ], coerce=int, default=1)
    through = RadioField('是否通过', choices=['是', '否'])
    recomment = TextAreaField('意见:',validators=[DataRequired()])
    submit = SubmitField("确认")



class RegisterForm(FlaskForm):
    username = StringField("账号",validators=[DataRequired(),Length(1, 20),
                                                   Regexp('^[a-zA-Z0-9]*$',
                                                          message='账号仅能包含a-z, A-Z,0-9.')])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField("确定")
    def validate_username(self, field):
        if Admin.query.filter_by(username=field.data).first():
            raise ValidationError('账号已存在')


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    category = SelectField('分类', coerce=int, default=1)
    obperson = SelectField('面向群体', choices=[
        (1, '内部'),
        (2, '公开'),
    ],coerce=int,default=1)

    body = CKEditorField('内容', validators=[DataRequired()])
    submit = SubmitField("提交")

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    name = StringField('名字', validators=[DataRequired(), Length(1, 30)])
    # status = SelectField('状态', choices=[
    #     (1, '使用中'),
    #     (9, '废弃'),
    # ], coerce=int, default=1)
    submit = SubmitField("提交")

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('名字已存在')

class MobanForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    body = CKEditorField('模板内容', validators=[DataRequired()])
    submit = SubmitField("提交")
