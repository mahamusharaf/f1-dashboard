with open('2026_drivers.txt', encoding='utf-16') as f:
    text = f.read()
with open('2026_drivers_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(text)
