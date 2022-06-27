def centerPoint_average(ptList):
    '''
    Calculate the average center of the specified point list
    @param ptList: List of points to calculate the average center from
    @type ptList: list
    '''
    # Calculate Center (Average)
    avgPt = [0, 0, 0]
    numPt = len(ptList)
    for pt in ptList:
        pos = glTools.utils.base.getPosition(pt)
        avgPt = [avgPt[0] + pos[0], avgPt[1] + pos[1], avgPt[2] + pos[2]]
    avgPt = [avgPt[0] / numPt, avgPt[1] / numPt, avgPt[2] / numPt]

    # Return Result
    return avgPt

# many more here: "https://programtalk.com/python-examples/glTools.utils.base.getPosition/"
