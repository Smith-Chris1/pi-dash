FROM python:3.8-slim

# Set the working directory within the container
WORKDIR /pi-dash

COPY app.py config.py requirements.txt location /pi-dash/
COPY /static/ /pi-dash/static/
COPY /templates /pi-dash/templates/

RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["/pi-dash/app.py"]