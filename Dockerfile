FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000


# Copy the binary file to the working directory
COPY AttestationClient /app/AttestationClient

# Set the binary file as executable
RUN chmod +x /app/AttestationClient

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]