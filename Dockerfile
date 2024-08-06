From python:3.8-slim

WORKDIR /app

COPY embeding_model/gte-small /app/embeding_model/gte-small
COPY requirements.txt /app/

# install dependencies
RUN pip install --upgrade pip
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# copy everything to the working directory
COPY . /app/

# expose streamlit port
EXPOSE 8501

ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "script/app.py"]