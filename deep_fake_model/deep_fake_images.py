import keras
from keras.preprocessing.image import load_img, img_to_array
from keras.applications.mobilenet_v2 import preprocess_input

model = None


def load_model():
    global model
    if model is None:
        print("Loading images model...")
        model = keras.models.load_model("../model.h5")

    return model


def is_fake(image_path):
    _model = load_model()
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))

    image = preprocess_input(image)

    predict = _model.predict(image)[0]
    print(predict)
    return predict[0] / sum(predict) > 0.5

    # print(f"Fake: {int(predict[0] / sum(predict) * 100)}%", end=", ")
    # print(f"Real: {int(predict[1] / sum(predict) * 100)}%")
