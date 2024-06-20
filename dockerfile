FROM python
RUN mkdir /chatbot
WORKDIR /chatbot
ADD . /chatbot
RUN pip install update
RUN apt-get install -y ffmpeg
RUN pip install -r requirements.txt
RUN chmod +x ./entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]