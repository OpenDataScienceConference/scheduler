from flask import Flask, make_response, request, jsonify
from collections import OrderedDict
import json
from unidecode import unidecode
import os
import pandas as pd
from csv import reader
import unidecode

app = Flask(__name__)

def transform(data):
    data['start time'] = data['date'] + ' ' + data['start time']
    data['start time'] = pd.to_datetime(data['start time'], format='%Y-%m-%d %H:%M:%S').astype(str)
    try:
        data['conference'] = data['conference'].map(lambda x: x.strip())
    except:
        pass
    data.sort_values(by = ['date', 'start time'], inplace = True)
    data['start time'] = data['start time'].map(lambda x: x[:10] + 'T' + x[11:])
    data_dict = OrderedDict()
    for date in data.date.unique():
        data_dict[date] = []
    for index, row in data.iterrows():
        row_dict = OrderedDict()
        row_dict['date'] = row['start time']
        row_dict['room'] = row['Room']
        row_dict['conference'] = row['Session']
        row_dict['title'] = row['Talk Title']
        #row_dict['title2'] = row['Talk Title2']
        row_dict['tags'] = [row['Tag 1 (Topic)'], row['Tag 2 (Technicality)'], row['Tag 3 (Difficulty)']]
        row_dict['speakers'] = [
            {'name': row['Speaker Name'], 'position': row['Position'], 'pictureUrl': row['pictureUrl'], 'link': row['link']}]
        #'detailUrl': row['detailUrl']
        data_dict[row['date']].append(row_dict)

    data_json = {"schedulerEvents": data_dict}
    return(data_json)

def encoding(r):
    return [a.encode('iso-8859-1') for a in r]

@app.route('/')
def form():
    return """
        <html>
            <body>
                <h1>CSV To JSON</h1>

                <form action="/transform" method="post" enctype="multipart/form-data">
                    <input type="file" name="data_file"/>
                    <input type="submit"/>
                </form>
            </body>
        </html>
    """

@app.route('/transform', methods=["POST"])
def transform_view():
    file = request.files['data_file']
    if not file:
        return "No file"

    file_contents = file.stream.read().decode("utf-8")
    file_contents = file_contents.replace('\r', '')
    file_contents = file_contents.split('\n')
    cols = file_contents[0].split(',')
    #print(list(reader(file_contents[1:]))[0])

    df_data = list(reader([unidecode.unidecode(x) for x in file_contents[1:]]))
    df = pd.DataFrame(df_data, columns = cols)
    result = transform(df)
    response = jsonify(result)
    #response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=odsc_east.json"
    return response

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
