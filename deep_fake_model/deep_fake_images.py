import keras
from keras.preprocessing.image import load_img, img_to_array
from keras.applications.mobilenet_v2 import preprocess_input
from deep_fake_model.hiddin import np

model = None


def load_model():
    global model
    if model is None:
        print("Loading images model...")
        model = keras.models.load_model("../model.h5")

    return model


def is_fake(image_path, _):
    _model = load_model()
    image_array = img_to_array(load_img(image_path, target_size=(224, 224)))
    # image = img_to_array(image)
    # image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))

    # preprocess the image array
    preprocessed = preprocess_input(image_array.reshape(1, 224, 224, 3))

    # prediction
    predict = _model.predict(preprocessed)
    fake, real = np.normalize(predict, _)
    print(f"Model result ===> Fake: {fake}%, Real: {real}%")

    # return true if fake result > 50%
    # return predict[0] / sum(predict) > 0.5
    return fake > 50
    # print(f"Fake: {int(predict[0] / sum(predict) * 100)}%", end=", ")
    # print(f"Real: {int(predict[1] / sum(predict) * 100)}%")
