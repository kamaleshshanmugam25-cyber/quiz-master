import os

public_dir = r"C:\A2757\QuizProject\frontend\public"
for root, dirs, files in os.walk(public_dir):
    rel = os.path.relpath(root, public_dir)
    print(f"Dir: {rel} ({len(files)} files)")
    if files:
        print("  Sample files:", files[:10])
