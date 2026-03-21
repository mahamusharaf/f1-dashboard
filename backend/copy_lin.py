import shutil
import os

src = r"C:\Users\Maha\.gemini\antigravity\brain\ba461998-3fc8-4238-8d5e-787d13115dfa\media__1774120186580.png"
dst = r"c:\Users\Maha\Desktop\f1-dashboard\frontend\public\lin.png"

try:
    shutil.copyfile(src, dst)
    print(f"Successfully copied image to {dst}")
except Exception as e:
    print("Error:", e)
