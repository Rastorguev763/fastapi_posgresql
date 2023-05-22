from fastapi import FastAPI
import requests
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Создание базы данных и таблицы
Base = declarative_base()

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(String)
    answer_text = Column(String)
    created_date = Column(DateTime, default=datetime.now)

engine = create_engine('sqlite:///questions.db')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# Модель данных для входного запроса
class QuestionRequest(BaseModel):
    questions_num: int

# POST метод для получения вопросов
@app.post("/questions")
def get_questions():
    # print('TUTUTUTUTUT')
    session = Session()
    questions = []
    # while len(questions) < 10:
    while len(questions) < 1:
        # Запрос к публичному API для получения случайного вопроса
        response = requests.get("https://jservice.io/api/random?count=1")
        # print(response)
        data = response.json()
        if response.status_code == 200 and data:
            question_data = data[0]
            question_text = question_data["question"]
            answer_text = question_data["answer"]
            print(f'question_data {question_data}, answer_text {answer_text}')

            # Проверка наличия вопроса в БД
            existing_question = session.query(Question).filter_by(question_text=question_text).first()
            if existing_question:
                continue

            # Сохранение вопроса в БД
            question = Question(question_text=question_text, answer_text=answer_text)
            session.add(question)
            session.commit()

            # Добавление вопроса в список
            questions.append(question)
    
    session.close()
    return questions

@app.get("/questions")
def get_all_questions():
    get_questions()
    session = Session()
    questions = session.query(Question).all()
    session.close()
    return questions
