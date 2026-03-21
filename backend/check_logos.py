import requests

urls = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Audif1.com_logo17_%28cropped%29.svg/512px-Audif1.com_logo17_%28cropped%29.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Cadillac_logo.svg/512px-Cadillac_logo.svg.png",
    "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/arvid-lindblad.jpg",
    "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/arvid-lindblad.jpg.transform/2col/image.jpg",
    "https://media.formula1.com/content/dam/fom-website/drivers/generic.jpg"
]

headers = {'User-Agent': 'Mozilla/5.0'}
for url in urls:
    try:
        res = requests.get(url, headers=headers, timeout=5)
        print(f"[{res.status_code}] {url}")
    except Exception as e:
        print(f"[ERR] {url} -> {e}")
