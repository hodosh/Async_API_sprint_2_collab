FROM docker.elastic.co/elasticsearch/elasticsearch:7.7.0


ENV APP_HOME=/home/es/
RUN mkdir $APP_HOME
WORKDIR $APP_HOME


# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

# run entrypoint.prod.sh
ENTRYPOINT ["/home/es/entrypoint.sh"]