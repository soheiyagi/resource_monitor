``` pip install psutil GPUtil python-dotenv requests setuptools ```

```
# .env
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your_webhook_id/your_webhook_token"
CPU_THRESHOLD=30.0  # 通知するCPU使用率の閾値（%）
GPU_THRESHOLD=20.0  # 通知するGPU使用率の閾値（%）
EXCLUDE_100_PERCENT=True # Trueにすると、100%のとき通知を除外
```


