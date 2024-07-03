import asyncio

import cv2

import bubbler
image = cv2.imread('uploads/94.png')
print(asyncio.run(bubbler.process_bubble(image, (0, 0))))