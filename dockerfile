FROM python
RUN mkdir /chatbot
WORKDIR /chatbot
ADD . /chatbot
RUN pip install update
RUN pip install -r requirements.txt
RUN apt-get update && \
 apt-get install -y \
    nodejs npm
RUN npm i azure-app-service-keepalive
EXPOSE 8080
ENTRYPOINT python chatbot.py ; node keepAlive.js