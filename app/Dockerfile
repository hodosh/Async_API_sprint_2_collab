###########
# BUILDER #
###########

# pull official base image
FROM python:3.9.13-slim as builder

# set work directory
WORKDIR /home/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libpq-dev python-dev gcc && \
    apt-get clean

# lint
RUN pip install --upgrade pip
RUN pip install flake8==3.9.2

COPY . .

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /home/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.9.13-slim

# create directory for the app user
WORKDIR /home/app

# create the app user
RUN addgroup --system app && adduser --system --no-create-home --group app
RUN chown -R app:app /home/app && chmod -R 755 /home/app

## create the appropriate directories
ENV HOME=/home/app
#ENV APP_HOME=/home/app/web
#RUN mkdir $APP_HOME
#RUN mkdir $APP_HOME/staticfiles
#RUN mkdir $APP_HOME/mediafiles
#WORKDIR $APP_HOME
#
#
## install dependencies
COPY --from=builder /home/app/wheels /wheels
COPY --from=builder /home/app/requirements.txt .
RUN pip install --no-cache /wheels/*
#
## copy entrypoint.sh
##COPY ./entrypoint.sh .
#RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
#RUN chmod +x  $APP_HOME/entrypoint.sh

# copy project
#COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app /home/app


# change to the app user - 
# FIX - need to grant propper permissions - don't work
USER app

#CMD gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --reload
# set permissions  - don't work?
# RUN chmod 755 $APP_HOME/*


# run entrypoint.prod.sh
#ENTRYPOINT ["/home/app/web/entrypoint.sh"]