import requests
import re

url = "https://www.formula1.com/en/drivers.html"
try:
    response = requests.get(url, timeout=10)
    # Target George Russell's card and find the image src
    # F1.com uses lazy loading or srcset usually
    content = response.text
    index = content.find("George Russell")
    if index != -1:
        # Look for the nearest src= or srcset=
        window = content[index-2000:index+1000]
        images = re.findall(r'src="([^"]+drivers[^"]+)"', window)
        images += re.findall(r'srcset="([^"]+drivers[^"]+)"', window)
        for img in set(images):
            print(f"Found: {img}")
    else:
        print("Driver not found in HTML")
except Exception as e:
    print(f"Error: {e}")
