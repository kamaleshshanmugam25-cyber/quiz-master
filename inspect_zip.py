import zipfile
import os

zip_path = r"C:\Users\academytraining.VDARTINC\.gemini\antigravity\brain\57a0eb6b-e674-4e94-be34-88bc25baa790\.user_uploaded\media_1795005429031_52dcb118.zip"
print(f"Zip exists: {os.path.exists(zip_path)}, size: {os.path.getsize(zip_path)}")

with zipfile.ZipFile(zip_path, 'r') as z:
    names = z.namelist()
    print(f"Total entries: {len(names)}")
    for n in names[:50]:
        print(f"  {n}")
