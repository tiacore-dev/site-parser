# Используем официальный образ Python в качестве базового
FROM python:3.12-slim

# Указываем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (важно!)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    gnupg \
    firefox-esr \
    xvfb \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libnss3 \
    libxss1 \
    libasound2 \
    libfontconfig1 \
    libxcb-shm0 \
    libxcb-render0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем GeckoDriver
RUN GECKODRIVER_VERSION="v0.33.0" && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" && \
    tar -xzf "geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" && \
    rm "geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" && \
    mv geckodriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver

# Устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Устанавливаем переменную окружения для Firefox headless
ENV MOZ_HEADLESS=1
