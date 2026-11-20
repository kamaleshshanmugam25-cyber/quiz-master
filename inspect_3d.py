import os

d = r"C:\A2757\QuizProject\frontend\public\Avatars_3d"
for f in os.listdir(d):
    p = os.path.join(d, f)
    print(f"{f}: {os.path.getsize(p)} bytes")
