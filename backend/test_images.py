import requests
import re
try:
    res = requests.get('https://www.formula1.com/en/drivers.html', timeout=10)
    # Search for something like /content/dam/fom-website/drivers/
    matches = re.findall(r'https://media\.formula1\.com/content/dam/fom-website/drivers/[^\"\'\s>\)]+', res.text)
    for m in set(matches):
        print(m)
except Exception as e:
    print(f"Error: {e}")
