from mtcnn import MTCNN


# Detect faces in an image using MTCNN
def detect_faces(image):
    detector = MTCNN()
    faces = detector.detect_faces(image)
    face_boxes = [(face['box'][0], face['box'][1], face['box'][2], face['box'][3]) for face in faces]
    # return list of coords (x, y, w, h) of the faces detected
    return face_boxes
