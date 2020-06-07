FROM python:3

ENV PYTHONUNBUFFERED=1
RUN pip3 install apscheduler==3.6.3 ring_doorbell==0.6.0
COPY app.py /app.py
WORKDIR /
CMD ["python3", "app.py"]

