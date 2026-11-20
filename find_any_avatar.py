import os, datetime

p = r"C:\Users\academytraining.VDARTINC\Downloads\avatars.zip"
if os.path.exists(p):
    t = os.path.getmtime(p)
    dt = datetime.datetime.fromtimestamp(t)
    print(f"Downloads/avatars.zip modified: {dt}, size={os.path.getsize(p)}")

# Also search whole C: drive for any other zip or avatar folders created in the last 2 days
for root, dirs, files in os.walk(r"C:\Users\academytraining.VDARTINC"):
    if any(x in root for x in ['node_modules', '.git', 'venv', 'AppData', '.vscode']):
        continue
    for f in files:
        if f.endswith('.zip') or ('avatar' in f.lower() and f.endswith(('.png', '.jpg', '.jpeg'))):
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                if sz > 1000:
                    print(f"Found: {fp} ({sz} bytes)")
            except:
                pass
