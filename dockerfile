FROM python
RUN mkdir /chatbot
WORKDIR /chatbot
ADD . /chatbot
RUN pip install update
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["/bin/sh", "-c" , "python chatbot.py && node keepAlive.js"]