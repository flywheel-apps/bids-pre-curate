FROM python:3.8-buster as base

LABEL maintainer="support@flywheel.io"

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}


# Save docker environ
ENV PYTHONUNBUFFERED 1

############## DEV ONLY ##########
#COPY user.json /root/.config/flywheel/user.json
# Copy executable/manifest to Gear
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py
COPY test_run.py ${FLYWHEEL}/test_run.py

# Configure entrypoint
RUN chmod a+x ${FLYWHEEL}/test_run.py
ENTRYPOINT ["/flywheel/v0/test_run.py"]
