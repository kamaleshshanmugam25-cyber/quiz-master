from PIL import Image
import os

d3d = r"C:\A2757\QuizProject\frontend\public\Avatars_3d"
d_old = r"C:\A2757\QuizProject\frontend\public\Avatars"

print("Comparison of Avatars vs Avatars_3d:")
for f in os.listdir(d3d):
    if f.endswith('.png'):
        p3d = os.path.join(d3d, f)
        p_old = os.path.join(d_old, f) if os.path.exists(os.path.join(d_old, f)) else None
        sz3d = os.path.getsize(p3d)
        sz_old = os.path.getsize(p_old) if p_old else "N/A"
        im3d = Image.open(p3d)
        print(f"{f}: 3D size={sz3d} ({im3d.size}), old size={sz_old}")
