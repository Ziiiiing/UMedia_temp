'''
The UMedia harvest script aims to find the newly added map items in the specific month.

No manually edit is needed before executing the script. However, at the beginning of the
execution, user needs to input the expected number of results as well as the selected 
year and date with the format like YYYY-MM. After that, the maps that were added in that 
date will be printed out in a csv spreadsheet with the action date you performed.

If you want to check the requested JSON data, you can uncomment the block cell, print the 
reqested data and read locally.


Original created on Dec 01, 2020
@author: Ziying/Gene Cheng (cheng904@umn.edu)

'''


import json
import time
import csv
import urllib.request

## user input
# number of map search results
num = input('Enter the number of results: ')
# assertion to check input format
assert num.isdigit() == True, 'Input number must be a integer.'

# specific year and month
yrmon = input('Enter the selected year and month(e.g. 2020-11): ')
# assertions to check input format: YYYY-MM
assert yrmon.count('-') == 1, 'Input format must be a dash-separated pair of year and month. '
assert len(yrmon.split('-')[0]) == 4, 'Input year must be 4 digits.'
assert len(yrmon.split('-')[1]) == 2, 'Input year must be 2 digits.'


# request map are sorted by latest added with the specific number of maps
req = f'https://umedia.lib.umn.edu/search.json?facets%5Bcontributing_organization_name_s%5D%5B%5D=University+of+Minnesota+Libraries%2C+John+R.+Borchert+Map+Library.&q=borchert&rows={num}&sort=date_added_sort+desc%2C+title_sort+asc'
res = urllib.request.urlopen(req)
data = json.loads(res.read())             

# Uncomment the following code block if you want to see the request json data locally
with open('request_data.json', 'w') as f:
    json.dump(data, f)
    print("#### Requested data is stored in request_data.json ####")


def NewItems(item):
    '''
    Function that extracts a list of specific metadata elements.

    Parameter
    ---------
    item: dictionary
        A dictionary refers to a map item with all metadata elements.

    Return
    ------
    metadataList: list
        A list stores all specific metadata elements for a map item.

    '''  
    identifier = item['system_identifier']
    slug = item['id']
    print(f'Collecting map id: {slug}')
    
    image = item['object']
    isPartOf =item['set_spec']
    parentId = item['parent_id']
    title = item['title']
    dateIssued = item['date_created'][0]
    types = 'Maps'
    formats = 'jpg'
    keyword = item['subject'][0]
    language = item['language'][0]
    accessRights = item['local_rights']
    iiif = f'https://cdm16022.contentdm.oclc.org/iiif/info/{isPartOf}/{parentId}/manifest.json'

    # some attributes may not exist in all map items    
    ## publisher
    try:
        publisher = item['publisher']
    except:
        publisher = ''

    ## creator
    try:
        creator = item['creator'][0]
    except:
        creator = ''

    ## description
    if 'description' in item:
        description = item['description']
    else:
        description = ''

    ## dimensions
    if 'dimensions' in item:
        dimensions = item['dimensions']
    else:
        dimensions = ''

    # 'descriptions' concatenates the 'description' and the 'dimensions' info
    descriptions = description + dimensions

    ## city/state/country
    spatialCoverage = ''
    if 'city' in item:
        city = item['city'][0]
        spatialCoverage += city
    if 'state' in item:
        state = item['state'][0]
        spatialCoverage += ','
        spatialCoverage += state
    if 'country' in item:
        country = item['country'][0]
        spatialCoverage += ','
        spatialCoverage += country

    ## if no city/state/country in the attribute, then use continent/region as the spatial coverage
    if not spatialCoverage:
        if 'continent' in item:
            continent = item['continent'][0]
            spatialCoverage = continent
        if 'region' in item:
            region =  item['region'][0]
            spatialCoverage = region


    metadataList = [identifier, slug, image, isPartOf, title, descriptions, dateIssued, 
                    creator, publisher, types, formats, keyword, language, 
                    spatialCoverage, accessRights, iiif]

    return metadataList


def printReport(path, fields, metadataList):
    '''
    Function that prints metadata fields and elements to a csv file.

    Parameters
    -----------
    path: str
        The output csv file path along with its file name.
    fields: list
        The field names of the output spreadsheet.
    metadataList: list
        The metadata content for newly added maps.
    
    '''
    with open(path, 'w', newline='', encoding='utf-8') as outfile:
        csvout = csv.writer(outfile)
        csvout.writerow(fields)      # fieldnames

        for item in metadataList:
            csvout.writerow(item)    # elements
        print("#### Report created ####")



# store all new added items' metadata
All_New_Items = []

# iterate through maps
for i in range(len(data)):    
    # find added month for each item
    add_time = data[i]['date_added']
    add_month = add_time[0:7]
    
    # compare added month with input month
    if add_month == yrmon:
        # collect metadata for this item
        metadataList = NewItems(data[i])
        All_New_Items.append(metadataList)

        
# fieldnames of output csv file
fieldnames = ['Identifier', 'Slug', 'Image', 'Is Part Of', 'Title', 'Description',
              'Date Issued', 'Creator', 'Publisher', 'Types', 'Format', 
              'Keyword', 'Language', 'Spatial Coverage', 'Access Rights', 'IIIF']        


# print csv spreadsheet with items that are added in that month
# add the action date to the output filename with the format (YYYYMMDD)
ActionDate = time.strftime('%Y%m%d')
filepath = "reports/allNewItems_%s.csv" % (ActionDate)
printReport(filepath, fieldnames, All_New_Items)