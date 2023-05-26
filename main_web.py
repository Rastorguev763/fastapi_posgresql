from fastapi import FastAPI, Body
import requests, time
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import FileResponse

app = FastAPI()

# Создание базы данных и таблицы
Base = declarative_base()

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_question = Column(Integer)
    question_text = Column(String)
    answer_text = Column(String)
    created_date = Column(DateTime, default=datetime.now)

# # создание sqlite 
# engine = create_engine('sqlite:///questions.sqlite')
# Base.metadata.create_all(bind=engine)
# Session = sessionmaker(bind=engine)

# Подключение и создание таблицы в PosgreSQL
# Замените значения на свои соответствующие параметры которые задавали при создания PostgreSQL
db_user = 'root'
db_password = 'root'
db_host = '127.0.0.1'
db_port = '5432'
db_name = 'postgres'
container_name = 'postgres_questions'

# Формируем строку подключения
# запуск с локальной машины
# db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# запуск с контейнера
db_url = f'postgresql://{db_user}:{db_password}@{container_name}/{db_name}'
engine = create_engine(db_url)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# POST метод для получения вопросов
@app.post("/questions")
def get_questions(data = Body()):
    question_last_add = sqlalchemy_to_json(get_all_questions())
    session = Session()
    num_question = int(data['num_questions'])
    # print(type(num_question))
    questions = []
    while len(questions) < num_question:
        
        try:
            # Запрос к публичному API для получения случайного вопроса
            
            response = requests.get("https://jservice.io/api/random?count=1")
            # print(response)
            data = response.json()
            if response.status_code == 200 and data:
                question_data = data[0]
                id_question =  question_data['id']
                question_text = question_data["question"]
                answer_text = question_data["answer"]

                # Проверка наличия вопроса в БД
                existing_question = session.query(Question).filter_by(id_question=id_question).first()
                if existing_question:
                    print(f'НАЙДЕН ПОВТОРЯЮЩИЙСЯ ВОПРОС №_{id_question}')
                    continue

                # Сохранение вопроса в БД
                question = Question(question_text=question_text, answer_text=answer_text, id_question=id_question)
                session.add(question)
                session.commit()

                # Добавление вопроса в список
                questions.append(question)
        except:
            print("Error\n"
                  "ПЫТАЮСЬ ПРОДОЛЖИТЬ РАБОТУ")
            time.sleep(10)
        print(f'ВСЕГО ДОБАВЛЕНО {len(questions)} ВОПРОСОВ, ПОСЛЕДНИЙ ДОБАВЛЕННЫЙ №_{id_question}')

    print(f'ВСЕГО ДОБАВЛЕНО {len(questions)} НОВЫХ ВОПРОСОВ')

    session.close()
    # print(type(question_last_add))
    return {"message": f"'ПОСЛЕДНИЙ ВОПРОС ЗАПИСАННЫЙ В ПРЕДЫДУЩЕМ ЗАПРОСЕ' - {question_last_add}"}

def get_all_questions():
    
    session = Session()
    questions = session.query(Question).order_by(desc(Question.id)).first()
    session.close()
    return questions

def sqlalchemy_to_json(my_object):
    # Преобразуем объект в словарь
    my_dict = my_object.__dict__

    # Удаляем некоторые ключи, которые не нужны
    keys_to_remove = ['_sa_instance_state', 'created_date']
    for key in keys_to_remove:
        my_dict.pop(key, None)

    return my_dict

@app.get("/")
def root():
    return FileResponse("public/main.html")

# для запуска сервера используйте команду
# uvicorn main_web:app --reload