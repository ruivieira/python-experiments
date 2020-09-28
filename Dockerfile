FROM fedora:32

RUN dnf group install "Development Tools" -y
RUN dnf install python3 python3-pip python3-devel -y
COPY requirements.txt /
RUN pip install -r requirements.txt
RUN mkdir /project