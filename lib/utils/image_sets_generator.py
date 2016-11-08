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


def generate_image_sets(xml_dir, image_sets_dir, val_portion=0.25):
    filename_list = os.listdir(xml_dir)

    print("Constructing {filename, {class_name: posneg}} dicts from files in xml_dir..")
    total_filename_classes_dict = {}   # {filename_wo_ext: {class_name: int}}
    class_name_set = set()
    filename_wo_ext_list = [''.join(filename.split('.')[:-1]) for filename in filename_list]
    for filename, filename_wo_ext in zip(filename_list, filename_wo_ext_list):
        total_filename_classes_dict[filename_wo_ext] = {}

        file_path = os.path.join(xml_dir, filename)
        root = etree.parse(file_path).getroot()
        object_name_elem_list = root.xpath(".//object/name")
        for object_name_elem in object_name_elem_list:
            class_name = object_name_elem.text
            if class_name not in class_name_set:
                class_name_set.add(class_name)
            if class_name not in total_filename_classes_dict[filename_wo_ext]:
                total_filename_classes_dict[filename_wo_ext][class_name] = 1

    print("Writing ImageSets txt file(s) for each class..")
    total_size = len(filename_wo_ext_list)
    valid_size = int(total_size * val_portion)
    random.shuffle(filename_wo_ext_list)
    valid_filename_wo_ext_list = sorted(filename_wo_ext_list[:valid_size])
    train_filename_wo_ext_list = sorted(filename_wo_ext_list[valid_size:])

    # Write filename_wo_ext lists to txt file for train/valid sets
    with open(os.path.join(image_sets_dir, "val.txt"), 'w') as fid:
        fid.writelines("%s\n" % line for line in sorted(valid_filename_wo_ext_list))
    with open(os.path.join(image_sets_dir, "train.txt"), 'w') as fid:
        fid.writelines("%s\n" % line for line in sorted(train_filename_wo_ext_list))

    # Write (filename_wo_ext, posneg) lists to txt file for train/valid set, for each class
    valid_fid_dict = {}
    train_fid_dict = {}
    for class_name in class_name_set:
        valid_fid_dict[class_name] = open(os.path.join(image_sets_dir, "%s_val.txt" % class_name), 'w')
        train_fid_dict[class_name] = open(os.path.join(image_sets_dir, "%s_train.txt" % class_name), 'w')

    for filename_wo_ext in valid_filename_wo_ext_list:
        for class_name in class_name_set:
            if class_name not in total_filename_classes_dict[filename_wo_ext]:
                valid_fid_dict[class_name].write("%s -1\n" % filename_wo_ext)
            else:
                valid_fid_dict[class_name].write("%s  1\n" % filename_wo_ext)

    for filename_wo_ext in train_filename_wo_ext_list:
        for class_name in class_name_set:
            if class_name not in total_filename_classes_dict[filename_wo_ext]:
                train_fid_dict[class_name].write("%s -1\n" % filename_wo_ext)
            else:
                train_fid_dict[class_name].write("%s  1\n" % filename_wo_ext)

    for class_name in class_name_set:
        valid_fid_dict[class_name].close()
        train_fid_dict[class_name].close()

    print("Done")


if __name__ == "__main__":
    data_dir = cfg.DATA_DIR
    args = parse_args()

    imdb_name = args.imdb_name
    xml_dir = os.path.join(data_dir, imdb_name, "Annotations")
    image_sets_dir = os.path.join(data_dir, imdb_name, "ImageSets", "Main")
    if not os.path.exists(image_sets_dir):
        os.makedirs(image_sets_dir)
    # test_portion = args.test_portion
    val_portion = args.val_portion

    generate_image_sets(xml_dir, image_sets_dir, val_portion)
