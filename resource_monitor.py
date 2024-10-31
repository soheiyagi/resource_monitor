import psutil
import GPUtil
import time
import requests
import socket
import subprocess
from dotenv import load_dotenv
import os

# .envファイルの読み込み
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CPU_THRESHOLD = float(os.getenv("CPU_THRESHOLD", 30.0))
GPU_THRESHOLD = float(os.getenv("GPU_THRESHOLD", 20.0))
EXCLUDE_100_PERCENT = os.getenv("EXCLUDE_100_PERCENT", "False").lower() == "true"

# ホスト名（端末名）を取得
HOSTNAME = socket.gethostname()

def send_discord_notification(message):
    """Discordに通知を送信"""
    data = {"content": f"[{HOSTNAME}] {message}"}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print(f"{HOSTNAME} からの通知が送信されました")
    else:
        print("Discord通知エラー:", response.status_code, response.text)

def is_container_running(container_name):
    """特定のコンテナが実行中か確認"""
    try:
        result = subprocess.run(["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                                capture_output=True, text=True, check=True)
        return container_name in result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Dockerコマンドのエラー: {e}")
        return False

def check_resource_usage():
    """CPUとGPUの利用率をチェックし、閾値を超えた場合に通知"""
    # 全コアの平均CPU使用率を取得
    cpu_usage_total = psutil.cpu_percent(interval=1, percpu=False)
    
    # メモリ使用率
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    
    # GPU使用率（NVIDIA GPUのみ対応）
    gpus = GPUtil.getGPUs()
    gpu_usage = max([gpu.load * 100 for gpu in gpus], default=0) if gpus else None

    # ログ出力
    print(f"Total CPU Usage: {cpu_usage_total}%, Memory Usage: {memory_usage}%")
    print(f"GPU Usage: {gpu_usage}%")

    # 特定のコンテナが実行中か確認
    if is_container_running("ray-arm_container_tmp"):
        print("ray-arm_container_tmpコンテナが実行中のため通知を除外")
        return

    # 100%除外の設定が有効で、現在のCPUまたはGPU使用率が100%なら通知を除外
    if EXCLUDE_100_PERCENT and (cpu_usage_total == 100 or gpu_usage == 100):
        print("100%使用率のため通知を除外")
        return

    # CPU利用率が閾値を超えた場合に通知
    if cpu_usage_total > CPU_THRESHOLD:
        send_discord_notification(f"警告：CPU使用率が{CPU_THRESHOLD}%を超えています！ 現在の使用率: {cpu_usage_total}%")

    # GPU利用率が閾値を超えた場合に通知
    if gpu_usage is not None and gpu_usage > GPU_THRESHOLD:
        send_discord_notification(f"警告：GPU使用率が{GPU_THRESHOLD}%を超えています！ 現在の使用率: {gpu_usage}%")

# 1分ごとに監視
while True:
    check_resource_usage()
    time.sleep(60)
