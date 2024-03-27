FROM python
RUN mkdir /chatbot
WORKDIR /chatbot
ADD . /chatbot
RUN pip install update
RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT python chatbot.py