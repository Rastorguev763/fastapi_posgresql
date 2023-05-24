from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String


# Замените значения на свои соответствующие параметры
db_user = 'root'
db_password = 'root'
db_host = '127.0.0.1'
db_port = '5432'
db_name = 'postgre'

# Формируем строку подключения
db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres'

# Создаем экземпляр Engine
engine = create_engine(db_url)

# Подключаемся к базе данных по умолчанию (postgres)
default_db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres'
default_engine = create_engine(default_db_url)

# Создаем базу данных "questions"
with default_engine.connect() as connection:
    connection.execute(f'CREATE DATABASE {db_name}')

# Подключаемся к созданной базе данных
db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(db_url)

# Создаем экземпляр Session
Session = sessionmaker(bind=engine)
session = Session()

# Создаем базу данных
Base = declarative_base()

# Определение моделей
class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    text = Column(String)

# Создаем таблицы
Base.metadata.create_all(engine)
