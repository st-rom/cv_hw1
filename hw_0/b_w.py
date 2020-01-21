import cv2
import numpy as np
from image_resize import image_resize

def main(file):
    rgb = (0, 255, 255)
    img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    
    img = image_resize(img, height=950)

    kernel = np.ones((5,5),np.uint8)
    changed = cv2.erode(img, kernel, iterations=3)
    changed = cv2.dilate(changed, kernel, iterations=3)

    ret, changed = cv2.threshold(changed, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    ind = np.argwhere(changed == 0)
    
    top_left = np.min(ind[:, 0]), np.min(ind[:, 1])
    btm_right = np.max(ind[:, 0]), np.max(ind[:, 1])


    r = changed[top_left[0]:btm_right[0], top_left[1]:btm_right[1]]
    resi2 = img[top_left[0]:btm_right[0], top_left[1]:btm_right[1]]
    cv2.imshow('image', resi2)
    while(1):
        if cv2.waitKey(10) == ord('q'):
            cv2.destroyWindow('image') 
            break
