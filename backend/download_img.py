import urllib.request
import os

url = "https://res.cloudinary.com/prod-f2f3/ar_1:1,c_fill,dpr_1.0,f_auto,g_auto,w_500/v1/f3/global/drivers/2024/03_Lindblad"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

out_path = r"c:\Users\Maha\Desktop\f1-dashboard\frontend\public\lin.png"
try:
    with urllib.request.urlopen(req) as response:
        img_data = response.read()
    with open(out_path, "wb") as f:
        f.write(img_data)
    print("Success. File size:", os.path.getsize(out_path))
except Exception as e:
    print("Failed:", e)
