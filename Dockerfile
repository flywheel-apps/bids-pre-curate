FROM python:3.8-buster as base

LABEL maintainer="support@flywheel.io"


# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Install dependencies
RUN pip install poetry
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install

# Save docker environ
ENV PYTHONUNBUFFERED 1

############## DEV ONLY ##########
#COPY user.json /root/.config/flywheel/user.json
# Copy executable/manifest to Gear
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py

# Configure entrypoint
RUN chmod a+x ${FLYWHEEL}/run.py
ENTRYPOINT ["pipenv","run","python3","/flywheel/v0/run.py"]

#ENTRYPOINT ["/bin/bash","-c"]
