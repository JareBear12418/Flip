from PyQt5.QtGui import QImage
from PIL import Image
import numpy as np

def numpyQImage(image):
    qImg = QImage()
    if image.dtype == np.uint8:
        if len(image.shape) == 2:
            channels = 1
            height, width = image.shape
            bytesPerLine = channels * width
            qImg = QImage(
                image.data, width, height, bytesPerLine, QImage.Format_Indexed8
            )
            qImg.setColorTable([qRgb(i, i, i) for i in range(256)])
        elif len(image.shape) == 3:
            if image.shape[2] == 3:
                height, width, channels = image.shape
                bytesPerLine = channels * width
                qImg = QImage(
                    image.data, width, height, bytesPerLine, QImage.Format_RGB888
                )
            elif image.shape[2] == 4:
                height, width, channels = image.shape
                bytesPerLine = channels * width
                fmt = QImage.Format_ARGB32
                qImg = QImage(
                    image.data, width, height, bytesPerLine, QImage.Format_ARGB32
                )
    return qImg
 
# generate data
im = Image.open('spritesheet.png').convert('RGB')
# Make into Numpy array of RGB and get dimensions
RGB = np.array(im)
h, w = RGB.shape[:2]

# Add an alpha channel, fully opaque (255)
RGBA = np.dstack((RGB, np.zeros((h,w),dtype=np.uint8)+255))

# Make mask of black pixels - mask is True where image is black
mBlack = (RGBA[:, :, 0:3] == [0,0,0]).all(2)

# Make all pixels matched by mask into transparent ones
RGBA[mBlack] = (0,0,0,0)
imarray = np.array(RGBA, dtype=np.uint8)
y,x = im.size

cropx = 174
cropy = 174

# TOP
TOP_LEFT        =   numpyQImage(imarray[0:0+cropy,0:0+cropx,:].copy())
TOP             =   numpyQImage(imarray[0:0+cropy,cropx:cropx+cropx,:].copy())
TOP_RIGHT       =   numpyQImage(imarray[0:0+cropy,cropx*2:cropx*2+cropx*2,:].copy())

# MIDDLE
MIDDLE_LEFT     =   numpyQImage(imarray[cropy:cropy+cropy,0:0+cropx,:].copy())
MIDDLE          =   numpyQImage(imarray[cropy:cropy+cropy,cropx:cropx+cropx,:].copy())
MIDDLE_RIGHT    =   numpyQImage(imarray[cropy:cropy+cropy,cropx*2:cropx*2+cropx*2,:].copy())

# BOTTOM
BOTTOM_LEFT     =   numpyQImage(imarray[cropy*2:cropy*2+cropy*2,0:0+cropx,:].copy())
BOTTOM          =   numpyQImage(imarray[cropy*2:cropy*2+cropy*2,cropx:cropx+cropx,:].copy())
BOTTOM_RIGHT    =   numpyQImage(imarray[cropy*2:cropy*2+cropy*2,cropx*2:cropx*2+cropx*2,:].copy())
