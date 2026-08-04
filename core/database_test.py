from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Text, DateTime, Boolean, and_, or_, not_, func, Table, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, backref
from sqlalchemy.sql import text
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# for postgres and other relational databases
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver:5432/db"
# SQLALCHEMY_DATABASE_URL = "mysql://username:password@localhost/db_name"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # only for sqlite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create base class for declaring tables
Base = declarative_base()

enrollments = Table(
    "enrollments",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("course_id", Integer, ForeignKey("courses.id")),
    Column("enrolled_date", DateTime(), default=datetime.now),
    UniqueConstraint("user_id", "course_id", name="unique_user_course_enrolled"),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30))
    email = Column(String())
    password = Column(String())
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    profile = relationship("Profile", backref="user", uselist=False)
    addresses = relationship("Address", backref="user")
    # addresses = relationship("Address", back_populates="user")
    posts = relationship("Post", backref="user")
    orders = relationship("Order", back_populates="user")
    courses = relationship("Course", secondary=enrollments, back_populates="attendees")

    def __repr__(self):
        return f"User(id: {self.id}, username: {self.username}, email: {self.email})"
    

"""
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(30))
    last_name = Column(String(30), nullable=True)
    age = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"User(id: {self.id}, first_name: {self.first_name}, last_name: {self.last_name})"
"""


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    # Alternative approach: remove the id column and use user_id as the primary key for a one-to-one relationship.
    # user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    first_name = Column(String())
    last_name = Column(String())
    bio = Column(Text(), nullable=True)

    def __repr__(self):
        return f"Profile(id: {self.id}, first_name: {self.first_name}, last_name: {self.last_name})"


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    city = Column(String())
    state = Column(String())
    zip_code = Column(String())

    # user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id: {self.id}, user_id: {self.user_id}, city: {self.city})"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String())
    content = Column(Text())

    created_date = Column(DateTime(), default=datetime.now)
    updated_date = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    comments = relationship("Comment", backref="post")

    def __repr__(self):
        return f"Post(id: {self.id}, title: {self.title})"


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    content = Column(Text())

    created_date = Column(DateTime(), default=datetime.now())

    # parent = relationship("Comment", back_populates="children", remote_side=[id])
    # children = relationship("Comment", back_populates="parent", remote_side=[parent_id])
    # Alternative approach: Use backref to define both parent and children relationships in a single declaration.
    children = relationship("Comment", backref=backref("parent", remote_side=[id]))

    def __repr__(self):
        return f"Comment(id: {self.id}, post_id: {self.post_id}, user_id: {self.user_id}, parent_id: {self.parent_id})"
    

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String())
    description = Column(Text())

    created_date = Column(DateTime(), default=datetime.now)

    attendees = relationship("User", secondary=enrollments, back_populates="courses")

    def __repr__(self):
        return f"Course(id: {self.id}, title: {self.title})"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Integer)

    user = relationship("User", back_populates="orders")


# to create tables and database
Base.metadata.create_all(engine)

session = SessionLocal()

session.add(User(username="John", email="john@gmail.com", password="123"))
session.commit()

user = session.query(User).filter_by(username="John").one_or_none()
print(user)

session.add(Course(title="Python", description="This is a Python course"))
session.commit()

python_course = session.query(Course).filter_by(title="Python").one()
print(python_course)

session.add(Course(title="FastApi", description="This is a FastApi course"))
session.commit()

fastapi_course = session.query(Course).filter_by(title="FastApi").one()
print(fastapi_course)

user.courses.append(python_course)
session.commit()

fastapi_course.attendees.append(user)
session.commit()

print(user.courses)
print(python_course.attendees)
print(fastapi_course.attendees)


""" Query for testing self-referencing relationship in the commit model
session.add(User(username="John", email="john@gmail.com", password="123"))
session.commit()

user = session.query(User).filter_by(username="John").one_or_none()

session.add(Post(user_id=user.id, title="Example title", content="Example content"))
session.commit()

post = user.posts[0]
session.add(Comment(user_id=user.id, post_id=post.id, content="this is a parent comment"))
session.commit()

parent_comment = post.comments[0]
session.add(Comment(user_id=user.id, post_id=post.id, parent_id=parent_comment.id, content="this is a reply comment"))
session.commit()

session.add(Comment(user_id=user.id, post_id=post.id, parent_id=parent_comment.id, content="this is a second reply comment"))
session.commit()

print(post.comments)
comments = session.query(Comment).filter_by(post_id=post.id, parent_id=None).all()
print(comments)

for comment in comments:
    print(comment.children)
"""


""" Query for testing one-to-one relationships between User and Profile models
session.add(User(username="John", email="john@gmail.com", password="123"))
session.commit()

user = session.query(User).filter_by(username="John").one_or_none()

try:
    session.add(Profile(user_id=user.id, first_name="John", last_name="Wood"))
    session.commit()
except Exception as e:
    session.rollback()
    print(e)

print(user.profile)
print(user.profile.first_name)
"""


""" Query for testing one-to-many relationships between tables
session.add(User(username="John", email="john@gmail.com", password="123"))
session.commit()

user = session.query(User).filter_by(username="John").one_or_none()
print(user)

addresses = [
    Address(user_id=user.id, city="city1", state="state1", zip_code="zipcode1"),
    Address(user_id=user.id, city="city2", state="state2", zip_code="zipcode2"),
]

session.add_all(addresses)
session.commit()

addresses = session.query(Address).filter_by(user_id=user.id).all()
address = session.query(Address).filter_by(user_id=user.id, city="city1").one_or_none()
print(addresses)
print(address)
print(address.user_id)
print(address.user) # This works because of the relationship
print(address.user.username)

print(user.addresses)
"""


""" CRUD query examples using filters, logical operators, aggregation, and raw SQL
# inserting data
John = User(first_name="John", age=44)
session.add(John)
session.commit()

# bulk insert
Max = User(first_name="Max", age=30)
Mika = User(first_name="Mika", age=33)
users = [Max, Mika]
session.add_all(users)
session.commit()

# retrieve all data
users_all = session.query(User).all()
print(users_all)

# retrieve data with filter
user = session.query(User).filter_by(first_name="John", age=44).first()
users = session.query(User).filter_by(first_name="John", age=44).all()
# user_3 = session.query(User).filter_by(first_name="John", age=44).one_or_none()
print(user, users)

# updating a record of data
user.last_name = "Wood"
session.commit()

# deleting a record of data
if user:
    session.delete(user)
    session.commit()

# queries with filter and where
users_filtered = session.query(User).filter(User.first_name=="John", User.age>=40).all()
print(users_filtered)
users_filtered = session.query(User).where(User.first_name=="John", User.age>=40).all()
print(users_filtered)
users_filtered = session.query(User).filter(User.first_name.like("%john%")).all()
print(users_filtered)
users_filtered = session.query(User).filter(User.first_name.ilike("%john%")).all()
print(users_filtered)
users_filtered = session.query(User).filter(User.first_name.like("John%")).all()
print(users_filtered)
users_filtered = session.query(User).filter(User.first_name.like("%John")).all()
print(users_filtered)
print(len(users_filtered))

# queries with and, or, not
users_filtered = session.query(User).filter(or_(User.first_name=="John", user.age>=40)).all()
print(users_filtered)
users_filtered = session.query(User).filter(and_(User.first_name=="John", user.age>=40)).all()
print(users_filtered)
users_filtered = session.query(User).filter(not_(User.first_name=="John")).all()
print(users_filtered)
users_filtered = session.query(User).filter(or_(not_(User.first_name=="John"), and_(User.age>35, User.age<60))).all()
print(users_filtered)

# queries with aggregate
total_users = session.query(func.count(User.id)).scalar()
print(total_users)
average_age = session.query(func.avg(User.age)).scalar()
print(average_age)
max_age = session.query(func.max(User.age)).scalar()
print(max_age)
min_age = session.query(func.min(User.age)).scalar()
print(min_age)

total_revenue = session.query(func.sum(Order.total_amount)).scalar()
print(total_revenue)

most_active_users = (
    session.query(
    User.first_name,
    func.count(Order.id).label("order_count")
    )
    .join(Order)
    .group_by(User.id, User.first_name)
    .order_by(func.count(Order.id).desc())
    .limit(5)
    .all()
)

print(most_active_users)

user_without_order = session.query(User).outerjoin(Order).filter(Order.id==None).all()
print([user.first_name for user in user_without_order])
print(user_without_order)

# queries with sql and not using orm
query = text("SELECT COUNT(*) FROM users WHERE age >= :min_age")
result = session.execute(query, {"min_age": 25}).scalar()
print(result)

query = text("SELECT * FROM users")
result = session.execute(query).fetchall()
print(result)
"""