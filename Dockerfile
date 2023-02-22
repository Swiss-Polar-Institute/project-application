FROM debian:bullseye-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
COPY requirements.txt entrypoint.sh tools/wait-for-mysql.sh /code/

RUN apt-get update && apt-get install --no-install-recommends --yes \
	python3-pip python3-setuptools \
	libmariadb-dev-compat libmariadb3 mariadb-client \
	python3-wheel python3-dev libpython3-dev \
    libjpeg-dev zlib1g-dev \
	gcc git \
	wkhtmltopdf
RUN pip3 install -r /code/requirements.txt
RUN apt-get purge -y libmariadb-dev-compat \
	gcc libpython3-dev && \
    apt-get autoremove -y && \
    apt-get clean
WORKDIR /code/ProjectApplication
ENTRYPOINT ["/code/entrypoint.sh"]
