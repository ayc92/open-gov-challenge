from flask import Flask, request, jsonify
import csv

app = Flask(__name__)

@app.route('/scrub/<file>', methods = ['POST'])
def file(file):
    # first upload the file, write it out to disk
    csv_file = request.files[file]
    csv_file.save('/tmp/temp.csv')
    # then open with csv module
    output_hash = { 'excel_rows_parsed': [],
                    'aggregations': {} }
    # field names will be stored here, so that we do not have to hardcode indices
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
                    fname = row[fields['Fund Name']]
                    did = int(row[fields['Department ID']])
                    dname = row[fields['Department Name']]
                    oname = row[fields['Object Name']]
                    amount = float(row[fields['Amount']])
                    if year in output_hash['aggregations']:
                        year_hash = output_hash['aggregations'][year]
                        # any necessary initialization
                        # if fund name or department name does not already exist in hash, add it
                        if fname not in year_hash['revenues']['funds']:
                            output_hash['aggregations'][year]['revenues']['funds'][fname] = 0.0
                        if fname not in year_hash['expenses']['funds']:
                            output_hash['aggregations'][year]['expenses']['funds'][fname] = 0.0
                        if dname not in year_hash['revenues']['departments']:
                            output_hash['aggregations'][year]['revenues']['departments'][dname] = 0.0
                        if dname not in year_hash['expenses']['departments']:
                            output_hash['aggregations'][year]['expenses']['departments'][dname] = 0.0
                        # add amounts
                        if amount > 0.0:
                            output_hash['aggregations'][year]['revenues']['funds'][fname] += amount
                            output_hash['aggregations'][year]['revenues']['departments'][dname] += amount
                            output_hash['aggregations'][year]['revenues']['total'] += amount
                        else:
                            output_hash['aggregations'][year]['expenses']['funds'][fname] += amount
                            output_hash['aggregations'][year]['expenses']['departments'][dname] += amount
                            output_hash['aggregations'][year]['expenses']['total'] += amount
                    else:
                        if amount > 0.0:
                            output_hash['aggregations'][year] = \
                                {'revenues': {'funds': {fname: amount}, 'departments': {dname: amount}, 'total': amount},
                                 'expenses': {'funds': {fname: 0.0}, 'departments': {dname: 0.0}, 'total': 0.0}}
                        else:
                            output_hash['aggregations'][year] = \
                                {'revenues': {'funds': {fname: 0.0}, 'departments': {dname: 0.0}, 'total': 0.0},
                                 'expenses': {'funds': {fname: amount}, 'departments': {dname: amount}, 'total': amount}}
            row_idx += 1
    # now we need to format the floats as fixed precision (rounded to the hundreths place)
    for yr in output_hash['aggregations']:
        year_hash = output_hash['aggregations'][yr]
        for fun in year_hash['expenses']['funds']:
            output_hash['aggregations'][yr]['expenses']['funds'][fun] = \
                float('%.2f' % round(year_hash['expenses']['funds'][fun], 2))
        for fun in year_hash['revenues']['funds']:
            output_hash['aggregations'][yr]['revenues']['funds'][fun] = \
                float('%.2f' % round(year_hash['revenues']['funds'][fun], 2))
        for dep in year_hash['expenses']['departments']:
            output_hash['aggregations'][yr]['expenses']['departments'][dep] = \
                float('%.2f' % round(year_hash['expenses']['departments'][dep], 2))
        for dep in year_hash['revenues']['departments']:
            output_hash['aggregations'][yr]['revenues']['departments'][dep] = \
                float('%.2f' % round(year_hash['revenues']['departments'][dep], 2))
        output_hash['aggregations'][yr]['expenses']['total'] = \
            float('%.2f' % round(year_hash['expenses']['total'], 2))
        output_hash['aggregations'][yr]['revenues']['total'] = \
            float('%.2f' % round(year_hash['revenues']['total'], 2))
    # time to jsonify and send the repsonse!
    return jsonify(**output_hash)

if __name__ == '__main__':
    app.debug = True
    app.run()