# author: jeff calkins
# date: 11-01-2020
# version: 1
#
# python3 usps_pdf2csv.py -f USPS_performance.pdf
#
# application parses the USPS performance PDF for every weekly row
# containing Area, District, Week and First-Class Mail column data
# after reading the entire document for Area & District for every week
# the application writes a single CSV line for an Area District, and
# outputs to STDOUT, a time series of statistics, for each week.
# associated with the Area & District time series, is a header noting
# a column for Area, for District and a column for each time value
#
# the application run on a MAC on python 3.7.9
# the application requires installing the PyPDF module
# sudo -H pip install PyPDF2

import re
import PyPDF2 
import argparse
import sys
from datetime import datetime

Areas = ['Capital Metro', 'Eastern', 'Great Lakes', 'Pacific', 'Northeast', 'Southern', 'Western']
headings = ['Area', 'District', 'Week', 'First-Class Mail']
FCMdataset = {}

def update_FCMdataset(a_data_point):
    [Area, District, Week,FirstClassMailSuccess] = a_data_point
    index = Area + District
    if index in FCMdataset:
        FCMdataset[Area+District].append(a_data_point) 
    else:
        FCMdataset[Area+District] = []
        FCMdataset[Area+District].append(a_data_point) 

def parse_a_page(result):
    length = len(result) 
    for i in range(length):
        if result[i] in Areas:
            line_list = result[i:i+4:1]
            stat = line_list[3].replace('%','') 
            stat = float(stat) / 100.0
            line_list[3] = '%1.4f' % stat 
            line = ",".join(line_list) 
            #print(line)
           
            update_FCMdataset(line_list)

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str,  required=True, help="file pdf name")
args = parser.parse_args()
fn = args.f

pdfFileObj = open(fn, 'rb') 
pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 

page_ct = pdfReader.numPages 

for page_number in range(page_ct):
    pageObj = pdfReader.getPage(page_number) 
    result = pageObj.extractText().splitlines()
    parse_a_page(result)

pdfFileObj.close()

header = False
for areas in FCMdataset:
    area_list = FCMdataset[areas]
    time_series = []
    buckets = []

    for point in area_list:
        [Area, District, Week, FirstClassMail] = point
        time_series.append(FirstClassMail)    
        buckets.append(Week)

    if header == False:
        buckets_line = ",".join(buckets)
        begin_string = "Area, District, " 
        print(begin_string, buckets_line)
        header = True

    time_series_line = ",".join(time_series)
    begin_string = Area + "," + District + ","  
    print(begin_string, time_series_line)
