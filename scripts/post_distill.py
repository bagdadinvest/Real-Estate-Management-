#!/usr/bin/env python3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(BASE_DIR, 'distill_output')
index_path = os.path.join(out_dir, 'index.html')

content = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Redirecting…</title>
  <meta http-equiv=\"refresh\" content=\"0; url=en/new/\">
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; padding: 2rem; color: #111; }
    a { color: #2563eb; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
  <script>
    (function(){
      var target = 'en/new/';
      try { window.location.replace(target); } catch (e) { window.location.href = target; }
    })();
  </script>
</head>
<body>
  <p>Redirecting to the English site… <a href=\"en/new/\">Click here if you are not redirected.</a></p>
</body>
</html>
"""

os.makedirs(out_dir, exist_ok=True)
with open(index_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Wrote {index_path}")

