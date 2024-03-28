FROM python
RUN mkdir /chatbot
WORKDIR /chatbot
ADD . /chatbot
RUN pip install update
RUN pip install -r requirements.txt
RUN chmod +x ./entrypoint.sh

EXPOSE 80
ENTRYPOINT ["./entrypoint.sh"]