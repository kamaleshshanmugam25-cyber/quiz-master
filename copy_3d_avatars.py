import shutil
import os

src_dir = r"C:\A2757\QuizProject\frontend\public\Avatars_3d"
dest_public = r"C:\A2757\QuizProject\frontend\public\Avatars"
dest_build = r"C:\A2757\QuizProject\frontend\build\Avatars"

os.makedirs(dest_public, exist_ok=True)
os.makedirs(dest_build, exist_ok=True)

for f in os.listdir(src_dir):
    if f.endswith('.png'):
        src_file = os.path.join(src_dir, f)
        dest1 = os.path.join(dest_public, f)
        dest2 = os.path.join(dest_build, f)
        shutil.copy2(src_file, dest1)
        shutil.copy2(src_file, dest2)
        print(f"Copied {f}: {os.path.getsize(dest1)} bytes to public & build")

print("Copy completed successfully!")
