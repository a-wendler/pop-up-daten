import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
import unicodedata
from lxml import etree

def dnb_sru(query):
    
    base_url = "https://services.dnb.de/sru/dnb"
    params = {'recordSchema' : 'MARC21-xml',
          'operation': 'searchRetrieve',
          'version': '1.1',
          'maximumRecords': '100',
          'query': query    
         }
    r = requests.get(base_url, params=params)
    xml = soup(r.content, 'lxml')
    records = xml.find_all('record', {'type':'Bibliographic'})
    
    if len(records) < 100:
        
        return records
    
    else:
        
        num_results = 100
        i = 101
        while num_results == 100:
            
            params.update({'startRecord': i})
            r = requests.get(base_url, params=params)
            xml = soup(r.content, 'lxml')
            new_records = xml.find_all('record', {'type':'Bibliographic'})
            records+=new_records
            i+=100
            num_results = len(new_records)
            
        return records

def parse_record(record):
    
    ns = {"marc":"http://www.loc.gov/MARC21/slim"}
    xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
    
    #idn
    idn = xml.xpath("marc:controlfield[@tag = '001']", namespaces=ns)
    try:
        idn = idn[0].text
    except:
        idn = 'fail'
    
    """ # umfang
    umfang = xml.xpath("marc:datafield[@tag = '300']/marc:subfield[@code = 'a']", namespaces=ns)
    
    try:
        umfang = umfang[0].text
        #umfang = unicodedata.normalize("NFC", umfang)
    except:
        umfang = "unkown" 
        
    meta_dict = {"idn":idn,
                 "umfang":umfang}"""
    
    return idn

def make_list(row):
    if len(str(row.ISBN)) > 0:
        return list(map(parse_record, dnb_sru(f'NUM={row.ISBN}')))

df = pd.read_csv('popups.csv', sep=';')

df['dnb-idns'] = df.apply(make_list, axis=1)
df.to_csv('2021-04-20-popups.csv', sep=';', index=None)