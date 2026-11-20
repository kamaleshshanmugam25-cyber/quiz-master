import os

src = r"C:\A2757\QuizProject\frontend\src"
for root, dirs, files in os.walk(src):
    for f in files:
        if f.endswith('.js'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                c = fp.read()
                if 'avatarOptions' in c:
                    print(f"Found in {f}")
