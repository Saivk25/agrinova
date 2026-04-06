import rasterio
import numpy as np
import cv2

with rasterio.open(r'C:\Agrinova hackathon\VIT Hackathon\orthomosaic_cog.tif') as src:
    img = src.read([1,2,3])  # RGB bands
    img = np.transpose(img, (1,2,0))

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"Found {len(contours)} contours")