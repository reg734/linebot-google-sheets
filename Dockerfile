FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt
COPY requirements.txt .

# 安裝依賴套件
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 複製應用程式檔案
COPY app.py .
COPY google_sheets_oauth.py .

# 暴露端口
EXPOSE 5000

# 設定環境變數
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 啟動指令
CMD ["python", "app.py"]