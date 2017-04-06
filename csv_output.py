import codecs
import unicodecsv
import os

class CSVOutput(object):
    def __init__(self, filename=None):
        self.output_dir = './output/'
        self.ensure_dir(self.output_dir)

        if filename is not None:
            self.init_unicodecsv(filename)

    def ensure_dir(self,directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def init_unicodecsv(self,filename=None):
        self.csv_fh = codecs.open(self.output_dir + filename, 'wb')
        self.csv_fh.write(u'\uFEFF'.encode('utf8'))
        self.csv_unicode_writer = unicodecsv.writer(self.csv_fh, encoding='utf-8')

    def write_row(self,row):
        self.csv_unicode_writer.writerow(row)

if __name__ == "__main__":
    c = CSVOutput('test_file.csv')
    row = ['testing','csv_output']
    c.write_row(row)
    print "ok, output to test_file.csv"
