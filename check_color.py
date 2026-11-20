from PIL import Image

im = Image.open(r"C:\A2757\QuizProject\frontend\public\Avatars\Professional.png")
colors = im.getcolors(maxcolors=100000)
# Sort by count
colors.sort(key=lambda x: x[0], reverse=True)
print("Top 10 colors in Professional.png:")
for count, color in colors[:10]:
    print(f"  count={count}: {color}")
