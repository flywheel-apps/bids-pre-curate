FROM python:3.8-buster as base

LABEL maintainer="support@flywheel.io"


# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}
RUN pip install pipenv
COPY Pipfile ./
COPY Pipfile.lock ./
RUN python3 -m pipenv install


# Save docker environ
ENV PYTHONUNBUFFERED 1

############## DEV ONLY ##########

# Copy executable/manifest to Gear
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py
COPY tests/ ${FLYWHEEL}/tests

# Configure entrypoint
ENTRYPOINT ["/bin/bash","-c"]
