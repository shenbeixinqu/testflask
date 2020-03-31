
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from bluelog import db
from bluelog.models import Admin, Category, Post

fake = Faker()


def fake_admin():
    admin = Admin(
        username='admin',
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='暂无')
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()
        )

        db.session.add(post)
    db.session.commit()



