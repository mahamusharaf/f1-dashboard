import requests

urls = [
    "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/1col/image.png",
    "https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/1col/image.png",
    "https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png"
]

for url in urls:
    try:
        res = requests.head(url, timeout=5)
        print(f"{url} -> {res.status_code}")
    except Exception as e:
        print(f"{url} -> Error: {e}")
