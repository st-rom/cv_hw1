import sys
import os
import b_w
import photos


if len(sys.argv) > 2:
    print('You have specified too many arguments')
    sys.exit()
    
elif len(sys.argv) < 2:
    print('Enter path to an image.\nExample: python main.py imgs_0/img_0.jpg')
    sys.exit()
    
elif not os.path.isfile(sys.argv[1]):
    print('Enter valid path to an image')
    sys.exit()
    
elif sys.argv[1].endswith('jpg'):
    b_w.main(sys.argv[1])
    
else:
    photos.main(sys.argv[1])
