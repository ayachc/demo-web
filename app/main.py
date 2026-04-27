from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api import books, orders
from app.core.config import settings
from app.core.logger import setup_logging


setup_logging()

app = FastAPI(title=settings.APP_NAME)
app.include_router(books.router)
app.include_router(orders.router)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <script src="https://cdn.tailwindcss.com"></script>
      <title>Omni-Bookstore</title>
    </head>
    <body class="bg-slate-100 text-slate-900">
      <main class="mx-auto max-w-2xl p-8">
        <h1 class="text-3xl font-bold">全能书店 Omni-Bookstore</h1>
        <p class="mt-2 text-slate-600">A tiny bookstore service for agent repair tests.</p>
        <div class="mt-6 flex flex-wrap gap-3">
          <button class="rounded bg-blue-600 px-4 py-2 text-white" onclick="call('/books')">List Books</button>
          <button class="rounded bg-red-600 px-4 py-2 text-white" onclick="call('/books/999')">Crash Book 999</button>
          <button class="rounded bg-emerald-600 px-4 py-2 text-white" onclick="call('/orders?book_id=1', 'POST')">Buy Book 1</button>
          <button class="rounded bg-amber-600 px-4 py-2 text-white" onclick="call('/books/1')">Load Comments</button>
        </div>
        <pre id="output" class="mt-6 min-h-40 overflow-auto rounded bg-white p-4 text-sm shadow"></pre>
      </main>
      <script>
        async function call(url, method = 'GET') {
          const output = document.getElementById('output');
          output.textContent = 'Loading ' + method + ' ' + url;
          try {
            const res = await fetch(url, { method });
            const text = await res.text();
            output.textContent = text;
          } catch (err) {
            output.textContent = err.stack || String(err);
          }
        }
      </script>
    </body>
    </html>
    """
