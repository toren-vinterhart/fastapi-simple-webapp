from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Boolean, and_, or_, not_, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import text

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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(30))
    last_name = Column(String(30), nullable=True)
    age = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"User(id: {self.id}, first_name: {self.first_name}, last_name: {self.last_name})"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey("users.id"))
    total_amount = Column(Integer)

    user = relationship("User", back_populates="orders")

# to create tables and database
Base.metadata.create_all(engine)

session = SessionLocal()

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
