import os
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
import string, random, requests
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
app = Flask(__name__)

#app.config.from_pyfile('config.py')
account = 'storagesamplescreateeys'   # Azure account name
key = 'S00GYHACh0JlvLK5/8iKU5mECGbRPnx15jxuJOAWrx230XAYfKOh6T0DmYmdoX1cz3GBRc8uzqJt+AStZPq0pw=='     # Azure Storage account access key  
container = 'storagesamples-rg' # Container name

service = BlobServiceClient(account_url="https://storagesamplescreateeys.blob.core.windows.net", container = 'uploads', credential=key)

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        name_cap = request.form.get('name')
        type_cap = request.form.get('type')
        filename = secure_filename(file.filename)
        filename_csv = 'upload_list.csv'
        fileextension = filename.rsplit('.',1)[1]
        email = name_cap.rsplit('@',1)[0]
        Randomfilename = id_generator()
        filename = Randomfilename + '.' + fileextension

        blob_client = service.get_blob_client(blob = filename, container = 'uploads')
        blob_client.upload_blob(file, blob_type="BlockBlob")

        blob_client_csv = service.get_blob_client(blob = filename_csv, container = 'uploads')
        container_client = service.get_container_client('uploads')

        with open("upload_list.csv", "wb") as my_blob:
            blob_data = blob_client_csv.download_blob()
            blob_data.readinto(my_blob)
        dataframe_blobdata = pd.read_csv("upload_list.csv")
        dataframe_blobdata = dataframe_blobdata.append({'date_time': datetime.now(), 'filename': filename, 'name': email}, ignore_index=True)
        output = dataframe_blobdata.to_csv (index=False, encoding = "utf-8")

        # Instantiate a new BlobClient
        blob_client = container_client.get_blob_client(filename_csv)
        # upload data
        blob_client.upload_blob(output, blob_type="BlockBlob", overwrite=True)

        return redirect(url_for('hello', name=name_cap, type = type_cap))      

    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello/<name>/<type>', methods=['GET', 'POST'])
def hello(name, type):
    if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name, type = type)
    else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('upload_file'))


if __name__ == '__main__':
   app.run()