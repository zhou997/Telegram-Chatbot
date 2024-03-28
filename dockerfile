FROM python
RUN mkdir /chatbot
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
WORKDIR /chatbot
ADD . /chatbot
RUN pip install update
RUN pip install -r requirements.txt

EXPOSE 80
ENTRYPOINT ['./entrypoint.sh']