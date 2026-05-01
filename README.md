# 资产借用和归还 Web 服务

这是一个轻量的资产借用/归还管理服务，包含 FastAPI 后端、原生前端页面和按用途拆分的日志模块。

## 功能

- 主页展示所有资产：图片、总量、剩余数量、借用人工号列表。
- 预置 4 个资产和初始借用状态。
- 支持添加资产、借用资产、归还资产。
- 每个请求带 `X-Request-ID`，便于串联前端请求、访问日志、业务日志和异常日志。
- 日志输出到：
  - `logs/app.log`
  - `logs/access.log`
  - `logs/error.log`

## 启动

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

浏览器访问：

```text
http://localhost:8000
```

## API

```text
GET  /health
GET  /api/assets
POST /api/assets
POST /api/assets/{asset_id}/borrow
POST /api/assets/{asset_id}/return
```

添加资产请求示例：

```json
{
  "asset_id": "KEYBOARD-001",
  "name": "机械键盘",
  "image_url": "https://example.com/keyboard.jpg",
  "total": 10
}
```

借用/归还请求示例：

```json
{
  "employee_id": "E1001"
}
```
