# Test writing real UTF-8 emojis
text = "🎮 📱 ⚡ 🕹️ ⏱️ 🎯 ✓ ▲ ◆ ● ■"
with open(r"C:\A2757\QuizProject\scratch\test_utf8.txt", "w", encoding="utf-8") as f:
    f.write(text)

with open(r"C:\A2757\QuizProject\scratch\test_utf8.txt", "r", encoding="utf-8") as f:
    read_back = f.read()

assert read_back == text
print("UTF-8 test successful:", read_back)
