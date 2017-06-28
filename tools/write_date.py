# -*- coding: utf-8 -*-

import csv
import optparse
import os
import logging
import codecs

TYPE = ""


def walk_dir(directory, function, exclude):
    maps = {}
    exclude_list = []
    if exclude:
        exclude_list = exclude.split(',')
    files = os.listdir(directory)
    files.sort()
    if not directory.endswith(os.sep):
        directory = directory + os.sep
    for item in files:
        full_path = directory + item
        if os.path.isdir(full_path):
            if item not in exclude_list:
                walk_dir(full_path, function, exclude)
        else:
            filename = directory + item
            if function:
                maps.update(function(filename))
    return maps


def read_maps(filename):
    maps = {}
    index = {}
    category_reader = csv.reader(file(filename, 'rb'))
    for line in category_reader:
        if not index:
            for i in range(len(line)):
                index[line[i]] = i
        else:
            if TYPE == "ZC":
                # key:domain; value:category,score,title
                maps[line[index["domain"]]] = [line[index["category"]],
                                               # line[index["score"]],
                                               line[index["title"]]]
            elif TYPE == "MID":
                maps[line[index["url"]]] = [line[index["业务标签"]],
                                               line[index["固定标签"]]]
    return maps


def main(options, args):
    global TYPE
    if os.path.isdir(args[0]):
        TYPE = "MID"
        head = ['业务标签', '固定标签']
        empty = ['', '']
        category_maps = walk_dir(args[0], read_maps, "")
    else:
        TYPE = "ZC"
        head = ['category', 'title']
        empty = ['', '']
        category_maps = read_maps(args[0])

    logging.info("Read category result success!")

    data_file = open(args[1], "rb")
    date_reader = csv.reader(data_file)
    date_writer = csv.writer(file(args[1].replace('.csv', '-cate.csv'), 'wb'))

    pv_main_index = {}
    for line in date_reader:
        if not pv_main_index:
            line += head
            for i in range(len(line)):
                pv_main_index[line[i]] = i
        elif category_maps.has_key(line[pv_main_index["url"]]):
            line += category_maps[line[pv_main_index["url"]]]
        else:
            line += empty
        date_writer.writerow(line)

    logging.info("Done!")


if __name__ == "__main__":
    option_parser = optparse.OptionParser(usage="Usage: %prog [options] resource-path")
    option_parser.add_option("-i", "--input", type='string',
                             default=None, help="input category file")

    options, args = option_parser.parse_args()

    if len(args) < 2:
        logging.fatal("Usage: write_date.py category.csv data.csv")
        exit(-1)

    main(options, args)
