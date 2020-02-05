# image-embedding-data

This file describes the format required to run csvToJson.py in order to
update the JSON files appropriately.



dataset*projection.csv


dataset -
    The display name of the dataset. This appears in
    the top left corner of the visualization. For
    example. "Particles - All"

projection -
    The display name of the projection. This appears
    in the top right corner of the visualization. For
    example. "L1 [64]"

In this example the full filename would be "Particles - All_L1 [64].csv"

The content of the file should be a csv file containing the following information.

The first row contains text labels for the columns. The columns should contain
the following.

column 1  - the X positions for all the points.
column 2  - the Y position for all the points.
column 3+ - any attribute that you want to visualize. This can be seen in the
            visualization in the top left, below the datasets, after the 
            attribute label.

So for the "Particles - All_L1 [64].csv" example, the first 5 lines of the file
could look like the following.

x,y,max_field,avg_field,scattering,extinction,absorption

3.87372,1.40561,3.34469,2.05705,-33.3863,-31.7639,-31.9838
-2.92122,-0.209223,1.02112,0.399764,-40.7863,-38.0932,-38.1633
-1.96136,-0.0598162,1.31549,0.569668,-38.251,-37.445,-38.0368
2.6516,-0.143876,2.65261,1.28398,-33.8529,-31.7579,-31.8892
