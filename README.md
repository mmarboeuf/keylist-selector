# Keyword selection toolkit

## What it is

This script selects the highest scoring keyword list from a list of input
keywords utilizing a multi-factor scoring model.

Input keywords and their metrics are read in from a file containing all
relevant information. The sample data for this script is real Apple App Store 
data scraped from ASO sites as of Dec 2014.

You can find a detailed description of how to select the right keywords
for your app on my blog here:

Part 1: How to find relevant keywords for your app
        http://blackboardmadness.com/blog/app-store-optimization-aso-selecting-the-right-keywords-part-1/
Part 2: Description of a basic keyword selection process
        http://blackboardmadness.com/blog/app-store-optimization-aso-selecting-the-right-keywords-part-2/
Part 3: Introduction to a multi-factor scoring model utilized in this script
        http://blackboardmadness.com/blog/app-store-optimization-aso-selecting-the-right-keywords-part-3/

Keyword metrics used in the multi-factor model:
Difficulty: How hard to rank for a keyword (0=easy, 10=hard to rank for)
Traffic: How high is keyword serach volume (0=no traffic, 10=high traffic)
Number of Apps: How many apps use a keyword (number >= 0)
Key length: Char length of a keyword    



## Notes

This toolkit requires Python3 to run due to Unicode support, if you want to use 
the code on Python 2, please use the solution as documented in the 
[Python csv module documentation](https://docs.python.org/2/library/csv.html):

```
import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
```

Just replace ```csv.reader()``` and ```csv.write()``` 
with ```UnicodeReader``` and ```UnicodeWriter```.

You will also need to add ```from io import open``` at the top of the file.