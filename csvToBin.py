import array

inFolder = './in/distMatrix/'

with open(inFolder + 'distMat_testcase.csv', 'rt') as f:
    rows = f.readlines()
    values = []
    for row in rows:
        entries = row.split(',')
        values.extend([float(x) for x in entries])
    # do a scalar here: if your input goes from [-100, 100] then
    #   you may need to translate/scale into [0, 2^16-1] for
    #   16-bit PCM
    # e.g.:
    #   values = [(val * scale) for val in values]

with open('distanceMatrix.bin', 'wb') as out:
    vals = array.array('f', values)
    vals.tofile(out)