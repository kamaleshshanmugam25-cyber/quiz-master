import os

user_up = r"C:\Users\academytraining.VDARTINC\.gemini\antigravity\brain\57a0eb6b-e674-4e94-be34-88bc25baa790\.user_uploaded"
for f in os.listdir(user_up):
    p = os.path.join(user_up, f)
    print(f"{f}: {os.path.getsize(p)} bytes")
