import asyncio

import cv2

import bubbler
image = cv2.imread('bubbles/bubble_13.jpg')
print(asyncio.run(bubbler.process_bubble(image, (0, 0))))