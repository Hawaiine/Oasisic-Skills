# 🥷 Stealth Browser Skill — Docker
#
# Multi-stage build: cache CloakBrowser binary in the image so
# every container starts with a ready-to-use stealth Chromium.
#
# Build:
#   docker build -t stealth-browser .
#
# Run (tier-1 probe):
#   docker run --rm stealth-browser
#
# Run (tier-2 probe with headed mode):
#   docker run --rm --shm-size=2g -e XVFB=1 \
#     -e PROXY="http://user:pass@residential:port" \
#     -e GEOIP=1 \
#     stealth-browser
#
# Run with persistent user data dir (cache CF cookies):
#   docker run --rm -v $PWD/user-data:/user-data \
#     -e PERSISTENT_DIR=/user-data \
#     stealth-browser python your-script.py
#
# Interactive shell:
#   docker run --rm -it --entrypoint bash stealth-browser

# === Stage 1: Install CloakBrowser ===
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir cloakbrowser
RUN cloakbrowser install
RUN rm -rf /root/.cache/pip

# === Stage 2: Runtime ===
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libatk-bridge2.0-0t64 \
    libatk1.0-0t64 \
    libgbm1 \
    libasound2t64 \
    xvfb \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /root/.cloakbrowser /root/.cloakbrowser

COPY scripts/ /opt/stealth-browser/scripts/
COPY references/ /opt/stealth-browser/references/
COPY PLAYBOOK.md /opt/stealth-browser/
COPY README.md /opt/stealth-browser/

WORKDIR /opt/stealth-browser
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python"]
CMD ["scripts/probe.py"]