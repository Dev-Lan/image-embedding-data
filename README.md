# image-embedding-data


# csvToJson.py
This script can be used to take input datasets as CSV files and update the json files used by the website.

For an input csv file the name of the file is used to set the labels on the website.

    dataset^projection.csv

dataset -
    The display name of the dataset. This appears in
    the top left corner of the visualization. For
    example. "Particles - All"

projection -
    The display name of the projection. This appears
    in the top right corner of the visualization. For
    example. "L1 [64]"

In this example the full filename would be "Particles - All^L1 [64].csv"

The content of the file should be a csv file containing the following information.

The first row contains text labels for the columns. The columns should contain
the following.

column 1  - the X positions for all the points.
column 2  - the Y position for all the points.
column 3+ - any attribute that you want to visualize. That is, these options will be available for coloring the points in the scatterplot, filtering in the scatterplot, or sorting in the image list.

So for the "Particles - All_L1 [64].csv" example, the first 5 lines of the file
could look like the following.

    x,y,max_field,avg_field,scattering,extinction,absorption
    3.87372,1.40561,3.34469,2.05705,-33.3863,-31.7639,-31.9838
    -2.92122,-0.209223,1.02112,0.399764,-40.7863,-38.0932,-38.1633
    -1.96136,-0.0598162,1.31549,0.569668,-38.251,-37.445,-38.0368
    2.6516,-0.143876,2.65261,1.28398,-33.8529,-31.7579,-31.8892

# examples.json

This file contains the list of datasets available on the website. This is not the data itself, but does contain metadata for each dataset. For a single dataset, the following information should be included:

| Attribute     | Description   |
| ------------- |:-------------:|
| *displayName*      | The name displayed on the website for this dataset. |
| *folderName*      | The name of the folder that contains the actual dataset data. |
| *imageWidth*      | The width in pixels of a single thumbnails. (all thumnails must be the same size) |
| *imageHeight*      | The height in pixels of a single thumbnails. (all thumnails must be the same size) |
| *distanceMatrixFilename*      | The path to the distance matrix .bin file. Since these are large, if they are shared across datasets they should be placed in the _shared_ folder. |
| *projectionList*      | The list of projections for the dataset. Each projection has two attributes, displayName and filename. The path is relative to the inside of folderName. |
| *displayName* (projectionList)     | The name displayed on the website for this projection. |
| *filename* (projectionList)     | The filename for the actual projection. Path is relative to the inside of folderName. |
    
# csvToBin.py
# renderSupershapes.py
# tileImages.py
