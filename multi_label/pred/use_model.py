import torch
import numpy as np
import torchvision.transforms as transforms
from PIL import Image


class Preproc(object):
    def __init__(self, sigma):

        self.sigma = sigma

    def __call__(self, sample):
        w, h = sample.size
        sample_numpy = np.array(sample)

        mean = np.mean(sample_numpy)
        std = np.std(sample_numpy)
        threshold = mean + std * self.sigma

        # Top to Bottom
        top_index = 0
        for index in range(int(h / 2)):
            if np.mean(sample_numpy[index, :, 0]) > threshold:
                top_index = index + 1
            else:
                break
        # Bottom to Top
        bottom_index = h - 1
        for index in range(h - 1, int(h / 2), -1):
            if np.mean(sample_numpy[index, :, 0]) > threshold:
                bottom_index = index - 1
            else:
                break
        # Left to Right
        left_index = 0
        for index in range(int(w / 2)):
            if np.mean(sample_numpy[:, index, 0]) > threshold:
                left_index = index + 1
            else:
                break
        # Right to Left
        right_index = w - 1
        for index in range(w - 1, int(w / 2), -1):
            if np.mean(sample_numpy[:, index, 0]) > threshold:
                right_index = index - 1
            else:
                break

        sample_numpy = sample_numpy[top_index:bottom_index + 1, left_index:right_index + 1]

        return Image.fromarray(sample_numpy)


class ToTensor(object):
    def __call__(self, sample):
        input_image = np.array(sample, np.float32) / 255.0
        input_image = input_image.transpose((2, 0, 1))
        return torch.from_numpy(input_image)


class Resize(object):
    def __init__(self, output_size):
        assert isinstance(output_size, (int, tuple))
        self.output_size = output_size

    def __call__(self, sample):
        new_h, new_w = int(self.output_size), int(self.output_size)

        sample = sample.resize((new_h, new_w), Image.BICUBIC)

        return sample


class Rescale(object):
    def __init__(self, output_size):
        assert isinstance(output_size, (int, tuple))
        self.output_size = output_size

    def __call__(self, sample):
        h, w = sample.size
        if isinstance(self.output_size, int):
            if h > w:
                new_h, new_w = self.output_size * h / w, self.output_size
            else:
                new_h, new_w = self.output_size, self.output_size * w / h
        else:
            new_h, new_w = self.output_size

        new_h, new_w = int(new_h), int(new_w)

        sample = sample.resize((new_h, new_w), Image.BICUBIC)

        return sample


IMAGE_SIZE = 224
OCT_model = torch.load('pred/model/OCT_model.pth').cuda()
fundus_model = torch.load('pred/model/fundus_model.pth').cuda()
OCT_cols = ['视网膜内液性暗腔', '视网膜下积液', 'RPE脱离', 'RPE下高反射病灶', '视网膜内或视网膜下高反射病灶',
            '尖锐的RPED峰', '双层征', '多发性RPED', 'RPED切迹', '视网膜内高反射硬性渗出']
fundus_cols = ['黄斑区视网膜出血', '黄斑区视网膜渗出', '黄斑区玻璃膜疣', '视网膜下橘红色病灶', '视网膜下出血']
OCT_test_tf = transforms.Compose([
    Preproc(0.2),
    Resize(IMAGE_SIZE),
    ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
fundus_test_tf = transforms.Compose([
    Preproc(0.2),
    Rescale(IMAGE_SIZE),
    transforms.CenterCrop(IMAGE_SIZE),
    ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def multi_label_classify(photo, img_type):
    if img_type == "OCT":
        model = OCT_model
        cols = OCT_cols
        test_tf = OCT_test_tf
    elif img_type == "fundus":
        model = fundus_model
        cols = fundus_cols
        test_tf = fundus_test_tf
    else:
        return []
    data = photo.convert('RGB')
    data = test_tf(data).unsqueeze(0).cuda()
    output = model(data)
    labels = []
    output = output.data.cpu().numpy() > 0.5
    for i in range(len(output[0])):
        if output[0, i] == np.True_:
            labels.append(cols[i])
    str_labels = ",".join(labels)
    if len(str_labels) == 0:
        return "未识别出体征"
    return str_labels
