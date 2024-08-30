import onnxruntime
import cv2
import numpy as np
import time


class Model:
    def __init__(self):
        self.img = None
        self.yolo = onnxruntime.InferenceSession("yolov8s.onnx")
        # tt = time.time()
        self.Siamese = onnxruntime.InferenceSession("siamese.onnx")
        # print(time.time() - tt)
        self.classes = ["big", "small"]
        self.color_palette = np.random.uniform(0, 255, size=(len(self.classes), 3))

    def detect(self, img: bytes):
        confidence_thres = 0.8
        iou_thres = 0.8
        model_inputs = self.yolo.get_inputs()
        input_shape = model_inputs[0].shape
        input_width = input_shape[2]
        input_height = input_shape[3]
        self.img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_ANYCOLOR)
        img_height, img_width = self.img.shape[:2]
        img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (input_height, input_width))
        image_data = np.array(img) / 255.0
        image_data = np.transpose(image_data, (2, 0, 1))
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)
        input = {model_inputs[0].name: image_data}
        output = self.yolo.run(None, input)
        outputs = np.transpose(np.squeeze(output[0]))
        rows = outputs.shape[0]
        boxes, scores, class_ids = [], [], []
        x_factor = img_width / input_width
        y_factor = img_height / input_height
        for i in range(rows):
            classes_scores = outputs[i][4:]
            max_score = np.amax(classes_scores)
            if max_score >= confidence_thres:
                class_id = np.argmax(classes_scores)
                x, y, w, h = outputs[i][0], outputs[i][1], outputs[i][2], outputs[i][3]
                left = int((x - w / 2) * x_factor)
                top = int((y - h / 2) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                class_ids.append(class_id)
                scores.append(max_score)
                boxes.append([left, top, width, height])
        indices = cv2.dnn.NMSBoxes(boxes, scores, confidence_thres, iou_thres)
        new_boxes = [boxes[i] for i in indices]
        small_imgs, big_img_boxes = {}, []
        for i in new_boxes:
            cropped = self.img[i[1]: i[1] + i[3], i[0]: i[0] + i[2]]
            if cropped.shape[0] < 35 and cropped.shape[1] < 35:
                small_imgs[i[0]] = cropped
            else:
                big_img_boxes.append(i)
        return small_imgs, big_img_boxes

    @staticmethod
    def preprocess_image(img, size=(105, 105)):
        img_resized = cv2.resize(img, size)
        img_normalized = np.array(img_resized) / 255.0
        img_transposed = np.transpose(img_normalized, (2, 0, 1))
        img_expanded = np.expand_dims(img_transposed, axis=0).astype(np.float32)
        return img_expanded

    def siamese(self, small_imgs, big_img_boxes):
        preprocessed_small_imgs = {i: self.preprocess_image(small_imgs[i]) for i in sorted(small_imgs)}
        result_list = []
        for i in sorted(preprocessed_small_imgs):
            image_data_1 = preprocessed_small_imgs[i]
            for box in big_img_boxes:
                if [box[0], box[1]] in result_list:
                    continue
                cropped = self.img[box[1]: box[1] + box[3], box[0]: box[0] + box[2]]
                image_data_2 = self.preprocess_image(cropped)
                inputs = {'input': image_data_1, "input.53": image_data_2}
                # tt = time.time()
                output = self.Siamese.run(None, inputs)
                # print(time.time() - tt)
                output_sigmoid = 1 / (1 + np.exp(-output[0]))
                res = output_sigmoid[0][0]
                # print("置信度: "+str(res))
                if res >= 0.1:
                    result_list.append([box[0], box[1]])
                    break
        for i in result_list:
            cv2.circle(self.img, (i[0] + 30, i[1] + 30), 5, (0, 0, 255), 5)
            cv2.imwrite("result.jpg", self.img)
        return result_list
