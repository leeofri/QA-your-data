# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container at /usr/src/app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Here --no-cache-dir is used to keep the Docker image as small as possible
RUN pip install --no-cache-dir -r requirements.txt

RUN argospm install translate-en_he && argospm install translate-he_en
RUN echo $(ls ~/.local/cache/argos-translate)
# Copy the current directory contents into the container at /usr/src/app
COPY . .

#init emmbeding on run time
RUN python init.py

VOLUME [ "/modules" ]
EXPOSE 8000

CMD ["chainlit","run","main_chainlid.py"]