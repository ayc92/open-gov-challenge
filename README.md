This is a Flask app that provides a HTTP endpoint ```POST http://<host>/scrub/:file```.

To run this app locally, you will probably want to install virtualenv.
First, make sure that you are in the project root (where the main <app>.py file is).
```sh
sudo pip install virtualenv
```
Then create a new Python virtualenv, and then we need to activate it.
```sh
virtualenv venv --distribute
source venv/bin/activate
```
Usually we would need to generate a ```requirements.txt``` file, but it already exists in the repository, so we're good!
Now that we have activated the virtualenv, we can run the Flask app via the following command.
```sh
python app.py
```

There are two versions, one that handles .xls input files, and another that handles .csv input files. The most up to date version (and the one that actually works correctly), is on the ```dev-csv``` branch, so from here on out, this document will refer to this version.

First, the input file is obtained from the parameters hash, and it is saved in to the temporary folder ```/tmp```. Then, the file is read from disk using Python's ```csv``` module.

Then, a csv reader instance is created to scan through the whole csv file. The first (or zeroth) row contains the fields, and these are put into a dictionary mapping each field name to its corresponding index within the row. This way, access of each field is not dependent on the order in which they appear in the csv file.

In terms of aggregations, there are two general cases:
    1. The year has already been placed into the output hash.
    2. The year has not yet been placed into the output hash.

Within each case, amounts are added or initialized accordingly, so that the format in the output json matches what is required. For each case, we must handle positive amounts and zero or negative amounts differently. The sign of the amount determines which value it is eventually added to.

After we finish parsing the csv file, some hacks are necessary in order to round the sums to the nearest hundreths, making them fixed precision numbers. This is to account for floating point errors when we do addition, which cause sums to turn into repeating decimals.

When this is done, we jsonify the dictionary and return it!