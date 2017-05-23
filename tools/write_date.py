import csv
import optparse
import logging
import codecs

if __name__ == "__main__":
    option_parser = optparse.OptionParser(usage="Usage: %prog [options] resource-path")
    option_parser.add_option("-i", "--input", type='string',
                             default=None, help="input category file")

    options, args = option_parser.parse_args()

    if len(args) < 2:
        logging.fatal("Usage: write_date.py category.csv data.csv")
        exit(-1)

    category_maps = {}
    category_index = {}
    category_reader = csv.reader(file(args[0], 'rb'))
    for line in category_reader:
        if not category_index:
            for i in range(len(line)):
                category_index[line[i]] = i
        else:
            # key:domain; value:category,score,title
            category_maps[line[category_index["domain"]]] = [line[category_index["category"]],
                                                             line[category_index["score"]],
                                                             line[category_index["title"]]]
    logging.info("Read category result success!")

    data_file = codecs.open(args[1], "rb", "utf-16")
    date_reader = csv.reader(data_file)
    date_writer = csv.writer(file(args[1].replace('.csv', '-cate.csv'), 'wb'))

    head = True
    for line in date_reader:
        if head:
            line += ['category', 'score', 'title']
            head = False
        elif category_maps.has_key(line[1]):
            line += category_maps[line[1]]
        date_writer.writerow(line)

    logging.info("Done!")
