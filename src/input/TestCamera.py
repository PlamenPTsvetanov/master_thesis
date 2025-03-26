# import cv2 as cv
# import numpy as np
# from PIL import Image
#
# face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
#
# img_pil = Image.open("car.jpeg")
# img = np.array(img_pil)
# img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
#
# gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#
# faces = face_cascade.detectMultiScale(gray, 1.1, 8)
# face_crops = []
# if len(faces) > 0:
#     max_face_size = max([w for (x, y, w, h) in faces])
#
#     for (x, y, w, h) in faces:
#         k = 0.3
#         pad = int(k * (max_face_size / w) * w)
#
#         x_pad = max(x - pad, 0)
#         y_pad = max(y - pad, 0)
#         w_pad = min(w + 2 * pad, img.shape[1] - x_pad)
#         h_pad = min(h + 2 * pad, img.shape[0] - y_pad)
#
#         # cv.rectangle(img, (x_pad, y_pad), (x_pad + w_pad, y_pad + h_pad), (255, 255, 0), 2)
#         face_crops.append(img[y_pad:y_pad + h_pad, x_pad:x_pad + w_pad])
#
#
# # cv.imshow('img', img)
# # for i, face in enumerate(face_crops):
# #     cv.imshow(f'Face {i+1}', face)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
