from flask import Flask, request, jsonify
# from flask.ext.restful import Resource, Api
import xlrd
# import json
from decimal import *

app = Flask(__name__)
# api = Api(app)

# class DataParser(Resource):
@app.route('/scrub/<file_name>', methods = ['POST'])
def parse(file_name):
    # amount should only be two decimal places
    # getcontext().prec = 2
    # first upload the file, write it out to disk,
    print 'before save'
    excel_file = request.files['file_name']
    excel_file.save('/tmp/temp.xls')
    print 'after save'
    # then open with xlrd
    excel_book = xlrd.open_workbook('/tmp/temp.xls')
    print 'after open workbook'
    excel_sheet = excel_book.sheet_by_index(0)
    print 'after open sheet'
    output_hash = { 'success': 'false',
                    'excel_rows_parsed': [],
                    'aggregations': {},
                    'name_lookup': {'funds': {}, 'departments': {}} }
    fields = {}
    for rownum in range(excel_sheet.nrows):
        row = excel_sheet.row_values(rownum)
        # 0th row is labels
        if rownum == 0:
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
            amount = row[fields['Amount']]
            if year in output_hash['aggregations']:
                if amount >= 0:
                    if fid in output_hash['aggregations'][year]['revenues']['funds']:
                        output_hash['aggregations'][year]['revenues']['funds'][fid] += amount
                    else:
                        output_hash['aggregations'][year]['revenues']['funds'][fid] = amount
                    if did in output_hash['aggregations'][year]['revenues']['departments']:
                        output_hash['aggregations'][year]['revenues']['departments'][did] += amount
                    else:
                        output_hash['aggregations'][year]['revenues']['departments'][did] = amount
                else:
                    if fid in output_hash['aggregations'][year]['expenses']['funds']:
                        output_hash['aggregations'][year]['expenses']['funds'][fid] += amount
                    else:
                        output_hash['aggregations'][year]['expenses']['funds'][fid] = amount
                    if did in output_hash['aggregations'][year]['expenses']['departments']:
                        output_hash['aggregations'][year]['expenses']['departments'][did] += amount
                    else:
                        output_hash['aggregations'][year]['expenses']['departments'][did] = amount
            else:
                if amount >= 0:
                    output_hash['aggregations'][year] = \
                        {'revenues': {'funds': {fid: amount}, 'departments': {did: amount}},
                         'expenses': {'funds': {}, 'departments': {}}}
                else:
                    output_hash['aggregations'][year] = \
                        {'revenues': {'funds': {}, 'departments': {}},
                         'expenses': {'funds': {fid: amount}, 'departments': {did: amount}}}
            if fid not in output_hash['name_lookup']['funds']:
                output_hash['name_lookup']['funds'][fid] = fname
            if did not in output_hash['name_lookup']['departments']:
                output_hash['name_lookup']['departments'][did] = dname
    print 'after loop'
    output_hash['success'] = True
    json_resp = jsonify(**{})
    try:
        json_resp = jsonify(**output_hash)
    except Exception as e:
        print e
    print 'after jsonify'
    return json_resp

# api.add_resource(DataParser, '/scrub/<string:file_name>', endpoint='parse')

if __name__ == '__main__':
    app.debug = True
    app.run()