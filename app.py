from flask import Flask, request, jsonify
# from flask.ext.restful import Resource, Api
# import xlrd
import csv
# import json
from decimal import *

app = Flask(__name__)

@app.route('/scrub/<file>', methods = ['POST'])
def file(file):
    # first upload the file, write it out to disk
    csv_file = request.files[file]
    csv_file.save('/tmp/temp.csv')
    # then open with csv module
    output_hash = { 'success': 'false',
                    'excel_rows_parsed': [],
                    'aggregations': {},
                    'name_lookup': {'funds': {}, 'departments': {}} }
    fields = {}
    with open('/tmp/temp.csv', 'rU') as csvfile:
        reader = csv.reader(csvfile)
        row_idx = 0
        for row in reader:
            # if row doesn't look like ['','','','',...,'']
            if filter(lambda x: x != '', row):
                # 0th row is labels
                if row_idx == 0:
                    for field in row:
                        fields[field] = row.index(field)
                else:
                    # add it to excel_rows_parsed
                    output_hash['excel_rows_parsed'].append(row)
                    # field values
                    year = int(row[fields['Year']])
                    month = row[fields['Month']]
                    fid = int(row[fields['Fund ID']])
                    if fid < 10:
                        fid = '0' + str(fid)
                    else:
                        fid = str(fid)
                    fname = row[fields['Fund Name']]
                    did = int(row[fields['Department ID']])
                    if did < 10:
                        did = '0' + str(did)
                    else:
                        did = str(did)
                    dname = row[fields['Department Name']]
                    oname = row[fields['Object Name']]
                    amount = float(row[fields['Amount']])
                    if year in output_hash['aggregations']:
                        if amount > 0:
                            if fname in output_hash['aggregations'][year]['revenues']['funds']:
                                output_hash['aggregations'][year]['revenues']['funds'][fname] += amount
                            else:
                                output_hash['aggregations'][year]['revenues']['funds'][fname] = amount
                            if dname in output_hash['aggregations'][year]['revenues']['departments']:
                                output_hash['aggregations'][year]['revenues']['departments'][dname] += amount
                            else:
                                output_hash['aggregations'][year]['revenues']['departments'][dname] = amount
                        else:
                            if fname in output_hash['aggregations'][year]['expenses']['funds']:
                                output_hash['aggregations'][year]['expenses']['funds'][fname] += amount
                            else:
                                output_hash['aggregations'][year]['expenses']['funds'][fname] = amount
                            if dname in output_hash['aggregations'][year]['expenses']['departments']:
                                output_hash['aggregations'][year]['expenses']['departments'][dname] += amount
                            else:
                                output_hash['aggregations'][year]['expenses']['departments'][dname] = amount
                    else:
                        if amount > 0:
                            output_hash['aggregations'][year] = \
                                {'revenues': {'funds': {fname: amount}, 'departments': {dname: amount}},
                                 'expenses': {'funds': {}, 'departments': {}}}
                        else:
                            output_hash['aggregations'][year] = \
                                {'revenues': {'funds': {}, 'departments': {}},
                                 'expenses': {'funds': {fname: amount}, 'departments': {dname: amount}}}
                    if fid not in output_hash['name_lookup']['funds']:
                        output_hash['name_lookup']['funds'][fname] = fname
                    if did not in output_hash['name_lookup']['departments']:
                        output_hash['name_lookup']['departments'][dname] = dname
            row_idx += 1
    output_hash['success'] = True
    json_resp = jsonify(**output_hash)
    return json_resp

if __name__ == '__main__':
    app.debug = True
    app.run()