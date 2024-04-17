# -*- coding: utf-8 -*-
"""TUGAS2_FASTER_RCNN_baf_edit0404.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KEnnYGL_nVndm034E7HhegBAHzyNIbw_

#Download COCO2017 data, split, and save dataset type as VOC dataset
"""

!pip install fiftyone
!pip install fiftyone-db-ubuntu2204

import os
import glob
from IPython.display import Image, display
from IPython import display
display.clear_output()

import fiftyone as fo
import fiftyone.utils.ultralytics as fou
import fiftyone.zoo as foz

ds_train = foz.load_zoo_dataset(
    "coco-2017",
    split="train",
    dataset_name="COCO-2017-train",
    label_types=["detections"],
    classes=["person"],
    shuffle=True,
    dataset_dir='./dataCOCO2017_',
    max_samples=4000,
    seed=43
)

ds_val = foz.load_zoo_dataset(
    "coco-2017",
    split="validation",
    dataset_name="COCO-2017-validation",
    label_types=["detections"],
    classes=["person"],
    shuffle=True,
    dataset_dir='./dataCOCO2017_',
    max_samples=500,
    seed=43
)

ds_test = foz.load_zoo_dataset(
    "coco-2017",
    split="validation",
    dataset_name="COCO-2017-test",
    label_types=["detections"],
    classes=["person"],
    shuffle=True,
    dataset_dir='./dataCOCO2017_',
    max_samples=500,
    seed=43
)

ds_test = foz.load_zoo_dataset(
    "coco-2017",
    split="test",
    dataset_name="COCO-2017-test",
    label_types=["detections"],
    classes=["person"],
    shuffle=True,
    dataset_dir='./dataCOCO2017_',
    max_samples=500,
    seed=43
)

def pickPersonLabel(dataset):
  # Iterate over the dataset
  for sample in dataset:
      # Get the detections
      detections = sample.ground_truth.detections
      # Filter out non-person detections
      detections = [d for d in detections if d.label == "person"]
      # Update the detections
      sample.ground_truth.detections = detections
      # Save the sample
      sample.save()

pickPersonLabel(ds_train)
pickPersonLabel(ds_val)
pickPersonLabel(ds_test)

train_classes = ds_train.distinct("ground_truth.detections.label")
val_classes = ds_val.distinct("ground_truth.detections.label")
test_classes = ds_test.distinct("ground_truth.detections.label")

print("train classes:", train_classes)
print("val classes:", val_classes)
print("test classes:", test_classes)

# VOC format requires a common classes list
classes = ds_train.distinct("ground_truth.detections.label")

ds_train.export(
    export_dir="/content/tmp/VOC_COCO2017_train",
    dataset_type=fo.types.VOCDetectionDataset,
    label_field="ground_truth",
    split="train",
    classes=classes,
)

ds_val.export(
    export_dir="/content/tmp/VOC_COCO2017_val",
    dataset_type=fo.types.VOCDetectionDataset,
    label_field="ground_truth",
    split="val",
    classes=classes,
)

ds_test.export(
    export_dir="/content/tmp/VOC_COCO2017_test",
    dataset_type=fo.types.VOCDetectionDataset,
    label_field="ground_truth",
    split="test",
    classes=classes,
)

!zip -r data.zip ./tmp/

from google.colab import drive
drive.mount('/content/drive')

!cp data.zip /content/drive/MyDrive

import matplotlib.pyplot as plt
from torchvision.io import read_image


image = read_image("/content/tmp/VOC_COCO2017_train/data/000000000360.jpg")

plt.figure(figsize=(16, 8))
plt.subplot(121)
plt.title("Image")
plt.imshow(image.permute(1, 2, 0))

"""#Upload and extract dataset"""

import zipfile
import os

# Mengganti 'path_to_zip_file' dengan path file ZIP yang diunggah di Google Colab
zip_file_path = '/content/drive/MyDrive/dataset_.zip'

# Mengganti 'extract_folder' dengan nama folder tempat hasil ekstraksi disimpan
extract_folder = '/content/drive/MyDrive'

# Membuat direktori baru untuk menyimpan file yang diekstrak
os.makedirs(extract_folder, exist_ok=True)

# Mengekstrak file ZIP
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)

# Mencetak daftar file yang telah diekstrak
extracted_files = os.listdir(extract_folder)
print("Files extracted:", extracted_files)

"""#Import requirements and define dataset location"""

import os
import collections
import pandas as pd
import numpy as np
import functools
import matplotlib.pyplot as plt
import cv2

from sklearn import preprocessing


import xml.etree.ElementTree as ET

import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2

import torch
import torchvision

from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.rpn import AnchorGenerator

from torch.utils.data import DataLoader, Dataset
from torch.utils.data import SequentialSampler

from google.colab import drive
drive.mount('/content/drive')

BASE_PATH = "/content/drive/MyDrive/dataset_/TRAIN_VAL"
XML_PATH = os.path.join(BASE_PATH, "/content/drive/MyDrive/dataset_/TRAIN_VAL/LABELS_TRAINVAL")
IMG_PATH = os.path.join(BASE_PATH, "/content/drive/MyDrive/dataset_/TRAIN_VAL/IMAGES_TRAINVAL")
XML_FILES = [os.path.join(XML_PATH, f) for f in os.listdir(XML_PATH)]

"""#Extract information, from xml files and make dataframe from extracted information"""

class XmlParser(object):

    def __init__(self,xml_file):

        self.xml_file = xml_file
        self._root = ET.parse(self.xml_file).getroot()
        self._objects = self._root.findall("object")
        # path to the image file as describe in the xml file
        self.img_path = os.path.join(IMG_PATH, self._root.find('filename').text)
        # image id
        self.image_id = self._root.find("filename").text
        # names of the classes contained in the xml file
        self.names = self._get_names()
        # coordinates of the bounding boxes
        self.boxes = self._get_bndbox()

    def parse_xml(self):
        """"Parse the xml file returning the root."""

        tree = ET.parse(self.xml_file)
        return tree.getroot()

    def _get_names(self):

        names = []
        for obj in self._objects:
            name = obj.find("name")
            names.append(name.text)

        return np.array(names)

    def _get_bndbox(self):

        boxes = []
        for obj in self._objects:
            coordinates = []
            bndbox = obj.find("bndbox")
            coordinates.append(np.int32(bndbox.find("xmin").text))
            coordinates.append(np.int32(np.float32(bndbox.find("ymin").text)))
            coordinates.append(np.int32(bndbox.find("xmax").text))
            coordinates.append(np.int32(bndbox.find("ymax").text))
            boxes.append(coordinates)

        return np.array(boxes)

def xml_files_to_df(xml_files):

    """"Return pandas dataframe from list of XML files."""

    names = []
    boxes = []
    image_id = []
    xml_path = []
    img_path = []
    for file in xml_files:
        xml = XmlParser(file)
        names.extend(xml.names)
        boxes.extend(xml.boxes)
        image_id.extend([xml.image_id] * len(xml.names))
        xml_path.extend([xml.xml_file] * len(xml.names))
        img_path.extend([xml.img_path] * len(xml.names))
    a = {"image_id": image_id,
         "names": names,
         "boxes": boxes,
         "xml_path":xml_path,
         "img_path":img_path}

    df = pd.DataFrame.from_dict(a, orient='index')
    df = df.transpose()

    return df

df = xml_files_to_df(XML_FILES)
df.head()

df_edit = df
df_edit

df_edit = df_edit[df_edit['names'] != 'dog']
df_edit

# check values for person class
df_edit['names'].value_counts()

# remove .jpg extension from image_id
df_edit['img_id'] = df_edit['image_id'].apply(lambda x:x.split('.')).map(lambda x:x[0])
df_edit.drop(columns=['image_id'], inplace=True)
df_edit.head()

# df['names'].values.tolist()

enc = preprocessing.LabelEncoder()
df_edit['labels'] = enc.fit_transform(df_edit['names'])
# df_edit['labels'] = np.stack(df_edit['labels'][i]+1 for i in range(len(df_edit['labels'])))

stacked_labels = []

# Loop melalui setiap array dalam kolom 'labels' dan tambahkan 1 ke setiap nilai
for labels_array in df_edit['labels']:
    modified_labels_array = labels_array + 1
    stacked_labels.append(modified_labels_array)

# Stack nilai-nilai yang sudah dimodifikasi
df_edit['labels'] = np.stack(stacked_labels)

classes = df_edit[['names','labels']].value_counts()
classes

df_edit

# make dictionary for class objects so we can call objects by their keys.
classes= {1:'person'}

range(len(df_edit['boxes']))

# bounding box coordinates point need to be in separate columns

df_edit['xmin'] = -1
df_edit['ymin'] = -1
df_edit['xmax'] = -1
df_edit['ymax'] = -1

df_edit[['xmin', 'ymin', 'xmax', 'ymax']] = df_edit['boxes'].apply(lambda x: pd.Series(x))

df_edit.drop(columns=['boxes'], inplace=True)
df_edit['xmin'] = df_edit['xmin'].astype(np.float64)
df_edit['ymin'] = df_edit['ymin'].astype(np.float64)
df_edit['xmax'] = df_edit['xmax'].astype(np.float64)
df_edit['ymax'] = df_edit['ymax'].astype(np.float64)

# drop names column since we dont need it anymore
df_edit.drop(columns=['names'], inplace=True)
df_edit.head()

len(df_edit['img_id'].unique())

"""#Separate train and validation data"""

image_ids = df_edit['img_id'].unique()
valid_ids = image_ids[-400:]
train_ids = image_ids[:-400]
len(train_ids)

valid_df = df_edit[df_edit['img_id'].isin(valid_ids)]
train_df = df_edit[df_edit['img_id'].isin(train_ids)]
valid_df.shape, train_df.shape

"""#Make dataset by dataset module"""

class VOCDataset(Dataset):

    def __init__(self, dataframe, image_dir, transforms=None):
        super().__init__()

        self.image_ids = dataframe['img_id'].unique()
        self.df = dataframe
        self.image_dir = image_dir
        self.transforms = transforms

    def __getitem__(self, index: int):
        image_id = self.image_ids[index]
        records = self.df[self.df['img_id'] == image_id]

        image = cv2.imread(f'{self.image_dir}/{image_id}.jpg', cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32)
        image /= 255.0
        rows, cols = image.shape[:2]

        boxes = records[['xmin', 'ymin', 'xmax', 'ymax']].values


        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        area = torch.as_tensor(area, dtype=torch.float32)

        label = records['labels'].values
        labels = torch.as_tensor(label, dtype=torch.int64)

        # suppose all instances are not crowd
        iscrowd = torch.zeros((records.shape[0],), dtype=torch.int64)

        target = {}
        target['boxes'] = boxes
        target['labels'] = labels
        # target['masks'] = None
        target['image_id'] = index
        target['area'] = area
        target['iscrowd'] = iscrowd

        if self.transforms:
            sample = {
                'image': image,
                'bboxes': target['boxes'],
                'labels': labels
            }
            sample = self.transforms(**sample)
            image = sample['image']

            target['boxes'] = torch.stack(tuple(map(torch.tensor, zip(*sample['bboxes'])))).permute(1,0)

            return image, target

    def __len__(self) -> int:
        return self.image_ids.shape[0]

def get_transform_train():
    return A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        ToTensorV2(p=1.0)
    ], bbox_params={'format':'pascal_voc', 'label_fields': ['labels']})

def get_transform_valid():
    return A.Compose([
        ToTensorV2(p=1.0)
    ], bbox_params={'format': 'pascal_voc', 'label_fields':['labels']})

def collate_fn(batch):
    return tuple(zip(*batch))

train_dataset = VOCDataset(train_df, IMG_PATH , get_transform_train())
valid_dataset = VOCDataset(valid_df, IMG_PATH, get_transform_valid())


# split the dataset in train and test set
indices = torch.randperm(len(train_dataset)).tolist()


train_data_loader = DataLoader(
    train_dataset,
    batch_size=4,
    shuffle=True,
    num_workers=4,
    collate_fn=collate_fn
)

valid_data_loader = DataLoader(
    valid_dataset,
    batch_size=4,
    shuffle=False,
    num_workers=4,
    collate_fn=collate_fn
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

"""#View sample"""

plt.figure(figsize=(20,20))
for i, box in enumerate(boxes):
    cv2.rectangle(sample,
                  (box[0], box[1]),
                  (box[2], box[3]),
                  (0, 0, 220), 2)
    class_name = classes[names[i]]
    cv2.putText(sample, str(class_name), (box[0], box[1] + 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 220, 0), 1, cv2.LINE_AA)

    plt.axis('off')
    plt.imshow(sample)