import os
import argparse
import random
from lxml import etree

from fast_rcnn.config import cfg

random.seed(2016)


def parse_args():
    """ Parse input arguments. """
    parser = argparse.ArgumentParser(description="ImageSets generator")
    parser.add_argument("--imdb_name", dest="imdb_name",
                        help="Image DB name containing XML files to be converted")
    # parser.add_argument("--test_portion", dest="test_portion",
    #                     help="Test data portion in the entire data",
    #                     default=0.2)
    parser.add_argument("--val_portion", dest="val_portion", type=float,
                        help="Validation data portion in the non-test data",
                        default=0.25)
    args = parser.parse_args()

    return args


def generate_image_sets(xml_dir, image_sets_dir, val_portion=None):
    filename_list = os.listdir(xml_dir)

    print("Constructing {class, file_list} dicts from files in xml_dir..")
    total_classes_dict = {}   # {class_name: {filename_wo_ext: int}}
    for filename in filename_list:
        filename_wo_ext = ''.join(filename.split('.')[:-1])
        file_path = os.path.join(xml_dir, filename)
        root = etree.parse(file_path).getroot()
        object_name_elem_list = root.xpath(".//object/name")
        for object_name_elem in object_name_elem_list:
            class_name = object_name_elem.text
            if class_name not in total_classes_dict:
                total_classes_dict[class_name] = {}
            total_classes_dict[class_name][filename_wo_ext] = 1

    print("Writing ImageSets txt file(s) for each class..")
    for class_name in total_classes_dict:
        filename_posneg_list = []
        for filename in sorted(filename_list):
            filename_wo_ext = ''.join(filename.split('.')[:-1])
            if filename_wo_ext in total_classes_dict[class_name]:
                filename_posneg_list.append("%s  1" % filename_wo_ext)
            else:
                filename_posneg_list.append("%s -1" % filename_wo_ext)
        with open(os.path.join(image_sets_dir, "%s_trainval.txt" % class_name), 'w') as wf:
            wf.writelines("%s\n" % line for line in filename_posneg_list)

        if val_portion:
            total_size = len(filename_posneg_list)
            valid_size = int(total_size * val_portion)
            random.shuffle(filename_posneg_list)
            with open(os.path.join(image_sets_dir, "%s_val.txt" % class_name), 'w') as wf:
                wf.writelines("%s\n" % line for line in sorted(filename_posneg_list[:valid_size]))
            with open(os.path.join(image_sets_dir, "%s_train.txt" % class_name), 'w') as wf:
                wf.writelines("%s\n" % line for line in sorted(filename_posneg_list[valid_size:]))

    print("Done")


if __name__ == "__main__":
    data_dir = cfg.DATA_DIR
    args = parse_args()

    imdb_name = args.imdb_name
    xml_dir = os.path.join(data_dir, imdb_name, "Annotations")
    image_sets_dir = os.path.join(data_dir, imdb_name, "ImageSets")
    if not os.path.exists(image_sets_dir):
        os.mkdir(image_sets_dir)
    # test_portion = args.test_portion
    val_portion = args.val_portion

    generate_image_sets(xml_dir, image_sets_dir, val_portion)
