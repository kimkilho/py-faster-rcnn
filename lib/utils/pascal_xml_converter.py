import os
import argparse
import shutil
from lxml import etree

from fast_rcnn.config import cfg


def parse_args():
    """ Parse input arguments. """
    parser = argparse.ArgumentParser(description="XML format converter")
    parser.add_argument("--imdb_name", dest="imdb_name",
                        help="Image DB name containing XML files to be converted")
    parser.add_argument("--xml_format_orig", dest="xml_format_orig",
                        help="XML format of files to be converted",
                        default="labelme")
    args = parser.parse_args()

    return args


def convert_labelme_to_pascal(imdb_name, xml_dir):
    filename_list = os.listdir(xml_dir)
    for filename in filename_list:
        file_path = os.path.join(xml_dir, filename)
        orig_root = etree.parse(file_path).getroot()
        root = etree.Element("annotation")

        # Add <folder> element
        folder_elem = etree.SubElement(root, "folder")
        folder_elem.text = imdb_name

        # Add <filename> element
        filename_elem = etree.SubElement(root, "filename")
        filename_elem.text = orig_root.xpath("./filename")[0].text

        # Add <source> element
        source_elem = etree.SubElement(root, "source")
        #   Add <database> sub-element
        source_database_elem = etree.SubElement(source_elem, "database")
        source_database_elem.text = "Sualab Database"
        #   Add <annotation> sub-element
        source_annotation_elem = etree.SubElement(source_elem, "annotation")
        source_annotation_elem.text = "Sualab %s" % imdb_name
        #   Add <image> sub-element
        source_image_elem = etree.SubElement(source_elem, "image")
        source_image_elem.text = "collected"

        # Add <size> element
        size_elem = etree.SubElement(root, "size")
        #   Add <width> sub-element
        size_width_elem = etree.SubElement(size_elem, "width")
        size_width_elem.text = orig_root.xpath("./imagesize/nrows")[0].text
        #   Add <height> sub-element
        size_height_elem = etree.SubElement(size_elem, "height")
        size_height_elem.text = orig_root.xpath("./imagesize/ncols")[0].text
        #   Add <depth> sub-element
        size_depth_elem = etree.SubElement(size_elem, "depth")
        size_depth_elem.text = "3"

        # Add <segmented> element
        segmented_elem = etree.SubElement(root, "segmented")
        segmented_elem.text = "1" if len(orig_root.xpath("//object/segm/scribbles")) > 0 else "0"

        # Add <object> elements
        object_orig_elem_list = orig_root.xpath(".//object")
        for object_orig_elem in object_orig_elem_list:
            # Add a single <object> element
            object_elem = etree.SubElement(root, "object")
            #   Add <name> sub-element
            object_name_elem = etree.SubElement(object_elem, "name")
            object_name_elem.text = object_orig_elem.xpath("./name")[0].text
            #   Add <pose> sub-element
            object_pose_elem = etree.SubElement(object_elem, "pose")
            object_pose_elem.text = "Unspecified"    # FIXME
            #   Add <truncated> sub-element
            object_truncated_elem = etree.SubElement(object_elem, "truncated")
            object_truncated_elem.text = "0"    # FIXME
            #   Add <occluded> sub-element
            object_occluded_elem = etree.SubElement(object_elem, "occluded")
            object_occluded_elem.text = "0"    # FIXME
            #   Add <difficult> sub-element
            object_difficult_elem = etree.SubElement(object_elem, "difficult")
            object_difficult_elem.text = "0"    # FIXME
            #   Add <bndbox> sub-element
            object_bndbox_elem = etree.SubElement(object_elem, "bndbox")
            object_bndbox_xmin_elem = etree.SubElement(object_bndbox_elem, "xmin")
            object_bndbox_xmin_elem.text = object_orig_elem.xpath("./segm/box/xmin")[0].text
            object_bndbox_ymin_elem = etree.SubElement(object_bndbox_elem, "ymin")
            object_bndbox_ymin_elem.text = object_orig_elem.xpath("./segm/box/ymin")[0].text
            object_bndbox_xmax_elem = etree.SubElement(object_bndbox_elem, "xmax")
            object_bndbox_xmax_elem.text = object_orig_elem.xpath("./segm/box/xmax")[0].text
            object_bndbox_ymax_elem = etree.SubElement(object_bndbox_elem, "ymax")
            object_bndbox_ymax_elem.text = object_orig_elem.xpath("./segm/box/ymax")[0].text

        os.remove(file_path)
        tree = etree.ElementTree(root)
        tree.write(file_path, pretty_print=True)


if __name__ == "__main__":
    data_dir = cfg.DATA_DIR
    args = parse_args()

    imdb_name = args.imdb_name
    xml_dir = os.path.join(data_dir, imdb_name, "Annotations")
    xml_format_orig = args.xml_format_orig

    if xml_format_orig == "labelme":
        convert_labelme_to_pascal(imdb_name, xml_dir)
