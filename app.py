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
    excel_file = request.files['file_name']
    excel_file.save('/temp.xls')
    # then open with xlrd
    excel_book = xlrd.open_workbook('/temp.xls')
    excel_sheet = excel_book.sheet_by_index(0)
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
            fname = row[fields['Fund Name']]
            did = int(row[fields['Department ID']])
            dname = row[fields['Department Name']]
            oname = row[fields['Object Name']]
            amount = Decimal(row[fields['Amount']])
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
                        output_hash['aggregations'][year]['expenses']['funds'][did] += amount
                    else:
                        output_hash['aggregations'][year]['revenues']['funds'][did] = amount
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
    output_hash['success'] = True
    json_resp = jsonify(**output_hash)
    return json_resp

# api.add_resource(DataParser, '/scrub/<string:file_name>', endpoint='parse')

if __name__ == '__main__':
    app.debug = True
    app.run()