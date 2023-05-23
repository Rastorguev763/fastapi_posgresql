from fastapi import FastAPI
import requests, time
# from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

engine = create_engine('sqlite:///questions.sqlite')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# Модель данных для входного запроса
# class QuestionRequest(BaseModel):
#     questions_num: int

# POST метод для получения вопросов
@app.post("/questions")
def get_questions(session, num_question):
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
    
    return questions

@app.get("/questions")
def get_all_questions(num_question: int):
    session = Session()
    questions = session.query(Question).order_by(desc(Question.id)).first()
    session.close()
    get_questions(session, num_question)
    return questions
