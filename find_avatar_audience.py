with open(r'C:\A2757\QuizProject\frontend\src\pages\AudienceDisplay.js', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        if 'avatar' in line.lower():
            print(f"{i+1}: {line.strip()[:100]}")
