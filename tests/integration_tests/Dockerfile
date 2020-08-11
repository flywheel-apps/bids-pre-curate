FROM python:3.8-buster as base

LABEL maintainer="support@flywheel.io"

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

COPY {Pipfile, Pipfile.lock} ./
RUN python3 -m pipenv install --system

# Save docker environ
ENV PYTHONUNBUFFERED 1

############## DEV ONLY ##########
#COPY user.json /root/.config/flywheel/user.json
# Copy executable/manifest to Gear
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py
COPY testd/ ${FLYWHEEL}/tests

# Configure entrypoint
ENTRYPOINT ["/bin/bash","-c"]
