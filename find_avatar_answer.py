with open(r'C:\A2757\QuizProject\frontend\src\pages\AnswerPage.js', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        if 'avatar' in line.lower() or 'renderavatar' in line.lower():
            print(f"{i+1}: {line.strip()[:100]}")
