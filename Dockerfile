FROM python:3.9
MAINTAINER Q9K
EXPOSE 8000
ENV PYTHONUNBUFFERED 1
COPY pip.conf /root/.pip/pip.conf
RUN mkdir -p /var/www/html/NoBC
WORKDIR /var/www/html/NoBC
ADD . /var/www/html/NoBC
RUN pip install -r requirements.txt
RUN chmod +x start.sh
CMD ["./start.sh"]
