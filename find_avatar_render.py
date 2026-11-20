import os

src = r"C:\A2757\QuizProject\frontend\src"
for root, dirs, files in os.walk(src):
    for f in files:
        if f.endswith('.js'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                c = fp.read()
                if 'rect x="35"' in c or 'faceGradient' in c or 'renderAvatar' in c or 'getAvatar' in c:
                    print(f"Match in: {f}")
