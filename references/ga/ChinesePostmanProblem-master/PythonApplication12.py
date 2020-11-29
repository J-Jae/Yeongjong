
#### Import library

import numpy as np
import matplotlib.pyplot as plt
import os
from os import listdir
import time


### for performance info
start_time = time.time()

def BuildMap(filename):
    ### BuildMap take a file with only data of this format ([stationIDA, stationIDB, distance])
    
    ### BuildMap return a square matrix with number of station ID of rows/elements. The element i,j is the distance between stationID i and stationID j.

    ### open file
    dictionaryLine = np.loadtxt(filename,comments = 'F',delimiter = ' ')


    ### we initialize parameter and output matrix
    numberstation = int(np.max(dictionaryLine[:,0:1])+1)
    mappingMetro = np.zeros((numberstation,numberstation))

    #for each line in the file ([stationIDA, stationIDB, distance])
    for i in range(len(dictionaryLine)):
        
        ### we assigne for the stationIDA column and stationIDB row the distance value (and the reverse)
        mappingMetro[int(dictionaryLine[i,0]),int(dictionaryLine[i,1])] = dictionaryLine[i,2]
        mappingMetro[int(dictionaryLine[i,1]),int(dictionaryLine[i,0])] = dictionaryLine[i,2]

    return mappingMetro

def BuildObjectiveMapHeuristicWay(filename_Dic,mappingMetro):
    ###filename_Dic is the name of the file containing the station dictionary (station ID, station name) (string)
    ### mappingMetro is the square matrix with number of station ID of rows/elements. The element i,j is the distance between stationID i and stationID j.
    
    ### intrastation is a list/array (need to verify) which contain the stationID of all the station inside Paris

    ### we first open filename_Dic
    f = open(filename_Dic, "r", encoding='UTF-8')
    #initialize stationDictionaryName (list)
    stationDictionaryName = list()
    ### for each line
    for line in f:
        ### we skip the ID part (it correspond to the line number anyway)
        cleanedLine = line[5:]
        ### we skip the \n caracter
        cleanedLine = cleanedLine[:-1]
        ### we split the string into word
        cleanedLine = cleanedLine.split()
        ### and we append this list to stationDictionaryName
        stationDictionaryName.append(cleanedLine)
    
    f.close()


    ### more initialization
    i = 0
    intraLimit = []
    ### for each line in stationDictionaryName
    for line in stationDictionaryName:
       
        ### if we find the word Porte
        if 'Porte' in line:
            ### you put the line number (which correspond to the station ID) into a list
            intraLimit.append(i)
            

        i = i+1

    ### we do a random walk with intraStation as a limit 
    ergodicPath,uselessStuff = randomWalk(70, 10000,1, 0.01, 4, mappingMetro, intraLimit, 'intraStation')

    ### we find all the station inside ergodicPath
    intraStation = np.unique(ergodicPath)

    #and we add the station ID in intraStation (because station with name porte are consider inside Paris)
    intraStation =np.sort(np.append(intraStation,intraLimit))



    ### the function return an array of 328 node which are or objective filter that will be used for the following step
    return intraStation


def CleanMatrix(finalAllPath,finalAllDist):
    ### this function eliminate the empty column (since when we initialize the outputMatrix, we created more row (we overshooted) to prevent not having enough
    ### space to put the whole path)

    ### finalAllPath,finalAllDist are the output matrix.
    minArray = Length(finalAllPath,'allPath')
    
    ### find the longest path (empty value not included)
    mostStationPath = int(np.max(minArray))
   
    ### we delete all the column which exceed the longest path
    finalAllPath = np.delete(finalAllPath,np.s_[mostStationPath:-1],axis = 1)
    finalAllDist = np.delete(finalAllDist,np.s_[(mostStationPath-1):-1],axis = 1)

    return finalAllPath, finalAllDist

def crossOver(allPathVectorA,allDistVectorA,allPathVectorB,allDistVectorB,choice):
    ### CrossOver do a permutation between two arrays,
    ### allPathVectorA,allPathVectorB are full numpy array (no element with value 1000) with a n and m element.
    ### allDistVectorA,allDistVectorB are full numpy array (no element with value 0) with a n-1 and m-1 element
    ### choice is a float with a value between 1 and 0

    ### crossOver return 4 new vectors resulting from the permutation
    
    # to identify the real length of the vector (if element = 1000, it mean that it is empty) 
    realLengthPathA = LengthPath(allPathVectorA)

    ### there is two kind of swapping, one of them is inside the body of the array
    ### if we change the body
    if choice > 0.1:
       

        ### it is a quality loop to avoid to pick a station which do not exist in the other path
        quality = False
        while quality == False :
        
        
            #### pick 2 stations in one path
            choiceA = np.sort(np.random.randint(0,realLengthPathA,size = 2))
            chosenStation_A1 = allPathVectorA[choiceA[0]] ### lowest indices
            chosenStation_A2 = allPathVectorA[choiceA[1]] ### highest indices
            

            if (len(np.where(allPathVectorB == chosenStation_A1)[0]) > 2) and (len(np.where(allPathVectorB == chosenStation_A2)[0]) > 2) and (np.abs(choiceA[0] - choiceA[1])>2) :

                quality = True

            #find same element
        ### pick in the path the same station ID
        choice_B1 = np.where(allPathVectorB == chosenStation_A1)[0][np.random.randint(0,len(np.where(allPathVectorB == chosenStation_A1)[0])-1)]
        choice_B2 = np.where(allPathVectorB == chosenStation_A2)[0][np.random.randint(0,len(np.where(allPathVectorB == chosenStation_A2)[0])-1)]

    

    #else, we are swapping head
    else:
        #this quality loop make sure that for a chosen station Id, we can find the same station in the other path
        choiceA = 2*[-1]
        quality = False
        while quality == False :

            #the only restriction is that the lower bound of the two subvector must match
            ### we select one random station in the first path
            choiceA[0] = np.random.randint(0,realLengthPathA)
            choiceA[1] = len(allPathVectorA)-1
            chosenStation = allPathVectorA[choiceA[0]]
            if  (len(np.where(allPathVectorB == chosenStation)[0]) > 1):
                quality = True
            
        ### we pick the same station in the other path
        choice_B1 = np.where(allPathVectorB == chosenStation)[0][np.random.randint(0,len(np.where(allPathVectorB == chosenStation)[0])-1)]
        choice_B2 = len(allPathVectorB)-1

    ## choiceA[0],choiceA[1],choice_B1,choice_B2 define the subarray that will be swap
    newPathVectorA,newDistVectorA,newPathVectorB,newDistVectorB = Swap(allPathVectorA,
                                                                       allDistVectorA,
                                                                       allPathVectorB,
                                                                       allDistVectorB,
                                                                       choiceA,
                                                                       choice_B1,
                                                                       choice_B2)   


    return newPathVectorA,newDistVectorA,newPathVectorB,newDistVectorB

def cutBadPath(temporaryPath,temporaryDist,intraStation):
    ### this function eliminate path which do not contain all the intraStation 

    ### temporaryPath/temporaryDist are the output matrix
    ### intraStation is the list of the StatioID of the station inside Paris

    ### the output are two new matrices newTemporaryPath and newTemporaryDist which contain all the path which cover all the station inside Paris.

    ### We created a two new outputMatrix 
    newTemporaryPath = np.full((len(temporaryPath[:,0]),len(temporaryPath[0,:])),1000)
    newTemporaryDist = np.full((len(temporaryDist[:,0]),len(temporaryDist[0,:])),0)


    ### for each path
    j = 0
    for i in range(len(temporaryPath[:,0])): 
            
        #look which station from intraStation are present
        mask = np.isin(intraStation,temporaryPath[i,:])  
        
        
        #if there is no station missing
        if len(np.where(mask==True)[0]) == len(intraStation):
            
            ### we put this path in the new OutputMatrix
            newTemporaryPath[j,0:len(temporaryPath[0,:])] = temporaryPath[i,:]
            newTemporaryDist[j,0:len(temporaryDist[0,:])] =  temporaryDist[i,:]

            j = j+1

    ### we cut eliminate the empty row of the newOutput matrix
    newTemporaryPath = newTemporaryPath[0:(j-1),:]
    newTemporaryDist = newTemporaryDist[0:(j-1),:]


    return newTemporaryPath,newTemporaryDist   

def deletion(allPathVectorA,allDistVectorA,allPathVectorB,allDistVectorB,choice):
    ### this function delete part of two path

    ### input allPathVectorA,allDistVectorA,allPathVectorB,allDistVectorB are array with empty element describing path 
    ### choice is a float between 0 and 1 which determine if the deletion affected the head or the body.

    ################################################################################################################
    # to identify the real length of the vector (if element = 1000, it mean that it is empty) 
    realLengthPathA = LengthPath(allPathVectorA)
    realLengthPathB = LengthPath(allPathVectorB) 
    ############################################################################################################### this part can be change (to optimize time)
     ### if deletion is done in body of the path
    if choice > 0.1 :

        # quality loop to prevent empty loop
        quality = False
        while quality == False :
      
            ## a number is well chosen if there is in each path more than 1 chosen station (same id number) in a path
            upperquality = False
            while upperquality == False:
                #select a random station for those two path
                choiceA = np.random.randint(0,realLengthPathA)
                chosenStationA = allPathVectorA[choiceA]
                choiceC = np.random.randint(0,realLengthPathB)
                chosenStationB = allPathVectorB[choiceC]

                if (len(np.where(allPathVectorB == chosenStationB)[0]) > 1) and (len(np.where(allPathVectorA == chosenStationA)[0]) > 1):
                    upperquality = True
            
            ### chose a step with the same station ID in order to get a close loop
            choiceB = np.where(allPathVectorA == chosenStationA)[0][np.random.randint(0,int(len(np.where(allPathVectorA == chosenStationA)[0])-1))]               
            choiceD = np.where(allPathVectorB == chosenStationB)[0][np.random.randint(0,int(len(np.where(allPathVectorB == chosenStationB)[0])-1))]
        

            if (np.abs(choiceC-choiceD) > 1) and (np.abs(choiceA-choiceB) > 1):
                quality = True
        
        #we delete the defined loop
        #if it is a close loop (we want to elimate step where nothing happen)

        ###myNewPathA[min([choiceA,choiceB]):(max([choiceA,choiceB]))] = []
        ###myNewDistanceA[(min([choiceA,choiceB])):(max([choiceA,choiceB]))] =  []

        lowerboundA = min([choiceA,choiceB])
        higherboundA = max([choiceA,choiceB])
        lowerboundB = min([choiceC,choiceD])
        higherboundB = max([choiceC,choiceD])

        myNewPathA = np.delete(allPathVectorA,np.s_[(lowerboundA+1):(higherboundA+1)]) # we keep only the first element of the loop Very IMPORTANT
        myNewDistanceA =  np.delete(allDistVectorA,np.s_[(lowerboundA):(higherboundA)])


        myNewPathB = np.delete(allPathVectorB,np.s_[(lowerboundB+1):(higherboundB+1)]) # we keep only the first element of the loop Very IMPORTANT
        myNewDistanceB =  np.delete(allDistVectorB,np.s_[(lowerboundB):(higherboundB)])
        

  
        

    ### if its not the body, it is the head, thus there is no longer the restriction of the loop.
    else :

        ### we choose one random station for each path
         choiceA = np.random.randint(0,realLengthPathA)
         choiceC =  np.random.randint(0,realLengthPathB)

         ### we cut everything after this step
         myNewPathA = np.delete(allPathVectorA,np.s_[choiceA+1:-1]) # we keep only the first element of the loop Very IMPORTANT
         myNewDistanceA =  np.delete(allDistVectorA,np.s_[choiceA:-1])

         myNewPathB = np.delete(allPathVectorB,np.s_[choiceC+1:-1]) # we keep only the first element of the loop Very IMPORTANT
         myNewDistanceB =  np.delete(allDistVectorB,np.s_[choiceC:-1])

    return myNewPathA,myNewDistanceA,myNewPathB,myNewDistanceB

def generation(allPath,allDist,numberOfEvents,intraStation,deathRate,mutationRatio,mappingMetro): 
    ### this function is a genetic algorithm. from path sample, we created mutation (crossover + mutation) and weed out the path that does not follow our condition

    ### allPath,allDist are the output Matrix which follow the following rule. allPath vector of one row is associate to allDist vector of the same row.
    ### All manipulation change allPath and allDist simultaneously to conserve consistency between the two vector. an array from all dist contain
    ### 1 element less than an array from allpath. Because of the framework of numpy, the length of each array are the same. However the length of the path 
    ### in the array is not necessarly the same. For all Path, an element with the value 1000 is considered empty. For alldist, and element with the value 0 is 
    ### considere empty.
    #
    ### numberOfEvents is an integer which indicate how many event the sample will have.
    ### deathRate is badly designe parameter and should be change
    ### lifeLine is a useless parameter and should be change
    ### mutationRatio is a float between 0 and 1 indicating the ratio swapping/deletion. 0 is for only deletion, 1 is for only swapping.
    #
    ### As output, generation give you another matrix with the same amount of row as allPath/allDist but not necessarly with the same number of columns.
    ### However, the output matrix follow the same rule as the input matrix ( we can iteratively use the function because of this) 



    ### creating a temporaryMatrix that will host the father and child 
    numberOfWalker = len(allPath[:,0])
    rowLengthPath = len(allPath[0,:])
    rowLengthDist = len(allDist[0,:])
    columnLength = int(numberOfWalker + 2*numberOfEvents)

    ### we created empty output matrix
    temporaryPath = np.full((columnLength, rowLengthPath*5), 1000)
    temporaryDist =  np.full((columnLength, rowLengthPath * 5 -1), 0)

    ### we keep the input path in the output matrix (parent might survive)
    temporaryPath[0:numberOfWalker,0:rowLengthPath] = allPath
    temporaryDist[0:numberOfWalker,0:rowLengthDist] = allDist

    ### we procede to the generation of children
    temporaryPath,temporaryDist = mutation(allPath,allDist,temporaryPath,temporaryDist,numberOfWalker,mutationRatio,mappingMetro)
    
    ### We discriminate hardly any new path which do not cover all station. 
    temporaryPath, temporaryDist = cutBadPath(temporaryPath,temporaryDist,intraStation)

    #### we need to discriminate the  other path we will do it with a probabilistic way with some weight which depend of the distance of each path.
    temporaryPath,temporaryDist = SurvivalTest(temporaryPath,temporaryDist)

    ### we want to cut the matrix so the number of column correspond to the longest number of step in the path collection chosen
    temporaryPath, temporaryDist = CleanMatrix(temporaryPath,temporaryDist)

    return temporaryPath,temporaryDist

def LengthPath(allPathVector):
    ### This function find the real length of a path (it ignore the 1000 value)

    ### allPathVector is an array from the output matrix

    ### it return realLengthOf path which is the real length of this path....


    ### by default, we assume that realLengthOfPath is the whole array (no empty element in the array)
    realLengthOfPath = len(allPathVector)
    ### if there is empty element in the array
    if len(np.where(allPathVector == 1000)[0]) > 0:

        ### we find the lowest indices of all the empty element.
        realLengthOfPath = np.min(np.where(allPathVector == 1000)[0])

    return realLengthOfPath

def Length(aMatrix,option):
    ### this function give the true length of an array (no empty element include). the function is more general in a sens that it accept matrix
    ### and vector and give the true length of an array whatever if it is a path array or a dist array (At the beginning the function was used to 
    ### test consistency between path array and his associated dist array (just to be sure that for n elements in path, we have n-1 elements in dist.)
    ### aMatrix is either a matrix or an array
    ### option is a string which help the function to recognize if it is dealing with a dist array or a path array.

    ### as output, minArray will be an array with the real length of each path in aMatrix


    #if it is a matrix

    if aMatrix.ndim > 1:

        ### if it is a matrix allPath
        if option == 'allPath':
            ### empty element are 1000
            iterationVectorUnique = np.unique(np.argwhere(aMatrix == 1000)[:,0])
            ### we find those empty element 
            iterationVector = np.argwhere(aMatrix == 1000)[:,0]
            positionVector = np.argwhere(aMatrix == 1000)[:,1]
            
        ### if it is a matrix allDist
        else:
            ### empty element are 0
            iterationVectorUnique = np.unique(np.argwhere(aMatrix == 0)[:,0])
            ### we find those empty element
            iterationVector = np.argwhere(aMatrix == 0)[:,0]
            positionVector = np.argwhere(aMatrix == 0)[:,1]

        minArray = np.full((len(aMatrix[:,0]),1),len(aMatrix[0,:]))

        ### for all path with empty element
        for x in iterationVectorUnique:
            ### we find the lowest indices with empty element and put this value in minArray
            rowSelected = np.argwhere(iterationVector == x)
            minArray[x] = np.min(positionVector[rowSelected])


    #if it is a vector
    else:
        
        ### if there is empty element 
        if len(np.argwhere(aMatrix == 1000)) != 0:

            ### if we deal with allPath vector
            if option == 'allPath':
                ### we find the lowest indices with element = 1000
                minArray = np.min(np.argwhere(aMatrix == 1000))
            else:
                 ### we find the lowest indices with element = 0
                minArray = np.min(np.argwhere(aMatrix == 0))
        ### if there is no empty element
        else:
            ### the distance is the length of aMatrix
            minArray = len(aMatrix)

    return minArray



def mutation(allPath,allDist,temporaryPath,temporaryDist,numberOfWalker,mutationRatio,mappingMetro):

    ### mutation will attribuated to chosen path a specific mutation and put it in the new output matrix (temporaryPath, temporaryDist)
    ### allPath,allDist are the output matrix (see in main where I describe the format of these data
    ### temporaryPath and temporaryDist is the new outputMatrix that will host all the path in allpath/alldist + the additionnal path resulting from
    ### the mutation. (integer matrix)
    ### numberOf walker is the number of path in allpath/alldist matrix . (integer)
    ### mutation Ratio is a float which has the value between 0 and 1 and allow us to tune the ratio deletion/mutation. 
    ### 0 mean that every event are deletion, 1 mean that every event are swap.


    ## find the empty line
    index = np.where(np.sum(allDist,axis = 1) == 0)[0]

    ### find the real length of each path (real length = no empty value include)
    realLengthPath = Length(allPath,'allPath').astype(int)
    realLengthDist = Length(allDist,'allDist').astype(int)


    ## create the seed for random event (each number say which rows will be affected) and the other vector will determine which event it is.
    ### this quality loop prevent that the event involve the same path. 
    quality = False
    while quality == False:
        event_Row = np.random.randint(0,int(len(allPath[:,0])-1),size = (numberOfEvents,2)) 

        if np.any(np.equal(event_Row[:,0],event_Row[:,1])) == False :
            quality = True
    ### create the seed that will determine what mutation will happen and if it is affecting the head or the body.
    event_Event = np.random.rand(numberOfEvents,2)

    j = 0
    #for each event
    for i in range(len(event_Event[:,0])):

        #if the row affected are not empty
        if len(np.where(np.isin(event_Row[i,:] , index) == True)[0]) == 0 :    

            ### if we roll higher than a certain number
            if event_Event[i,0] > mutationRatio:


                #it is a deletion
                myNewPathA,myNewDistanceA,myNewPathB,myNewDistanceB  = deletion(allPath[event_Row[i,0],0:int(realLengthPath[event_Row[i,0]]-1)],
                                                                                allDist[event_Row[i,0],0:int(realLengthDist[event_Row[i,0]]-1)],
                                                                                allPath[event_Row[i,1],0:int(realLengthPath[event_Row[i,1]]-1)],
                                                                                allDist[event_Row[i,1],0:int(realLengthDist[event_Row[i,1]]-1)],
                                                                                event_Event[i,1])
                
                ###we put the children path in the outputMatrix
                temporaryPath[2*j+numberOfWalker,0:len(myNewPathA[:])] = myNewPathA
                temporaryDist[2*j+numberOfWalker,0:len(myNewDistanceA[:])] = myNewDistanceA
                temporaryPath[(2*j+1)+numberOfWalker,0:len(myNewPathB[:])] = myNewPathB
                temporaryDist[(2*j+1)+numberOfWalker,0:len(myNewDistanceB[:])] = myNewDistanceB
                

                    

            #else 
            else :           
                

                #it is crossOver
                myNewPathA,myNewDistanceA,myNewPathB,myNewDistanceB = crossOver(allPath[event_Row[i,0],0:int(realLengthPath[event_Row[i,0]]-1)],
                                                                                allDist[event_Row[i,0],0:int(realLengthDist[event_Row[i,0]]-1)],
                                                                                allPath[event_Row[i,1],0:int(realLengthPath[event_Row[i,1]]-1)],
                                                                                allDist[event_Row[i,1],0:int(realLengthDist[event_Row[i,1]]-1)],
                                                                                event_Event[i,1])
                ### the childrenPath are put in the outputMatrix
                temporaryPath[2*j+numberOfWalker,0:len(myNewPathA[:])] = myNewPathA
                temporaryDist[2*j+numberOfWalker,0:len(myNewDistanceA[:])] = myNewDistanceA
                temporaryPath[(2*j+1)+numberOfWalker,0:len(myNewPathB[:])] = myNewPathB
                temporaryDist[(2*j+1)+numberOfWalker,0:len(myNewDistanceB[:])] = myNewDistanceB
                
            j = j+1

    return temporaryPath,temporaryDist

def randomWalk(initialPosition, numberOfIteration, numberOfWalker, roamingParameter, tabouLength, map, intraLimit, option):
    ### location is the starting point (integer)
    ### number of iteration is the number of step in a random direction (integer)
    ### number of walker is the number of random path created (integer)
    ### roaming parameter is a factor which penalized going back to the orignal position (integer...I have tuned this parameter to work correctly, do not touch)
    ### tabouLength is the length of the list which kept record the previous station occupied (integer... also do not suppose to be touched)
    ### matrix 375X375 where each row/column represent a station ID. Each element in the matrix represent the distance between the i station and j station.
    ### 0 value mean that there is no connection !!!
    ### intraLimit is a list of station ID which will be consider by a walker like a wall (0 probability to go through)
    ### this parameter is used to determined heuristically which station are inside paris. 
    ### option activated the functionality of intraLimit , if it is 'intraStation', it is activated, else, the walker walk freely 

    ### The randomWalk return two matrix (numpy array) with numberOfIteration columns and numberOfWalker row. 

    ### initialize futur output and parameter
    allPath = np.full((numberOfWalker,numberOfIteration+1),1000)
    allDistance = np.full((numberOfWalker,numberOfIteration),0)    
    roamingParameterVector = np.arange(1,tabouLength)
    roamingParameterVector = np.exp(-1* roamingParameter*(tabouLength-roamingParameterVector-1))


    j = 0
    #for each walker
    while j < numberOfWalker:
      
        pathSingle = np.full((1,numberOfIteration+1),1000)
        distanceSingle = np.full((1,numberOfIteration),0)

        pathSingle[0] = initialPosition
        location = initialPosition
        tabou = np.full((1,tabouLength),1000)
        #for each step
        for i in range(0,numberOfIteration):

            #we first look at neighbor station
            lineMetro = mappingMetro[location,:]
            neighborStation = np.where(lineMetro > 0)[0]
            neighborDistance = lineMetro[neighborStation]
 
            #we roll a random number for each neighbor
            choiceVector = np.random.rand(1,len(neighborStation))  ####### Verify the output of choiceVector !!!!

            #we look in the tabou list and we created a penalty vector (full 1 array)
            tabouDetection = np.isin(neighborStation, tabou )
            penaltyVector = np.full((1,len(neighborStation)),1, dtype= int)[0]

            #if there is a neighbor in the taboulist, in the corresponding element of penaltyVector, we put a number determine by the position of the neighbor
            #in the taboulist (see roamingVector)
            if len(np.where(tabouDetection==True)[0]) != 0 :
                x = np.where(tabouDetection==True)[0]
                x.astype(int)
                selectingPenalty = np.isin(tabou,neighborStation)
                
                y = np.where(selectingPenalty==True)[0]
                y.astype(int)
                penaltyVector[x[0]] = roamingParameterVector[y[0]]       
                     
            ### by multiplying penaltyVector with choiceVector, station previously visited has lower number
            choiceVector = choiceVector*penaltyVector

            ### if we are in the modality intraStation and if there is one neighbor which is in the intraLimit list (all station with the name porte)
            if option == 'intraStation' and np.any(np.isin(neighborStation,intraLimit)):
                
                ### we set the number related to this station to -1 (lowest possible)
                choiceVector[0][np.where(np.isin(neighborStation,intraLimit) == True)[0]] = -1

            ### we choose the highest number (all penalization favor the walker to go to new station and if the option is right, prevent the walker to go
            ### to any porte.
            choice =np.argmax(choiceVector[0])

            ### we update the new location of the walker
            location = neighborStation[choice]

            ### we write the information in the output matrix
            pathSingle[0,i+1] = location
            distanceSingle[0,i] = neighborDistance[choice]

            #and we update tabou list


            tabou = np.append(pathSingle[0,i+1],tabou)
            tabou = np.delete(tabou, tabouLength) 


        ### for each row, we look if all the intramuraux station have been explored


        mask = np.isin(intraLimit,pathSingle)
        if (np.all(mask) and option != 'intraStation') or (option == 'intraStation') :
            allPath[j,:] = pathSingle
            allDistance[j,:] = distanceSingle
            j = j+1




    return allPath, allDistance

def SurvivalTest(temporaryPath,temporaryDist):
    ### Survival test selected the 100 best path.
    ### temporary Path and temporaryDist are the outputmatrix
    ### lifeLine is a useless parameter and should be remove. 
    ### I could also use numberOfWalker as parameter and put it instead of 100

    #we created the seed
    randomSeed = np.random.rand(1,len(temporaryPath[:,0]))

    #we calculate the cumulative distance of each path
    sumDist = np.sum(temporaryDist,axis = 1)

    #from this, we calculated a penaltyFactor (the function work, but should be tuned more rigourously)
    lifeFactor = np.power(10,0)*np.exp(-1*0.000001*(sumDist))
        
    #we calculate the result of the test
    ### the survivalTest is done in such way that have short distance path have a highest lifeFactor and hence, has a higher chance of survival than
    ### longer path. The addition of randomseed allow us to keep some bad result which might contain a part of a good solution.
    survivalResult = -1*(lifeFactor+1*randomSeed) #I multiply by -1 because I want argsort to sort from highest value to lowest value
    survivalResult = np.transpose(survivalResult)   
    

    #we select the top 100
    finalAllPath = temporaryPath[np.argsort(survivalResult,axis = 0)[0:100],:]
    finalAllDist = temporaryDist[np.argsort(survivalResult,axis = 0)[0:100],:]
    finalAllPath = np.squeeze(finalAllPath, axis=1)
    finalAllDist = np.squeeze(finalAllDist, axis=1)

    return finalAllPath, finalAllDist


def Swap(newPathVectorA,newDistVectorA,newPathVectorB,newDistVectorB,choiceA,choice_B1,choice_B2):
    ### this function swap part of two different paths (ie. suppose vector A (A1 A2 A3) and vector B (B1 B2 B3)
    ### we define subvector A2 and B2 and swap them. We have in the end (A1 B2 A3) and (B1 A2 B3).

    ### newPathVectorA,newDistVectorA,newPathVectorB,newDistVector B are two rows from respectively allPath/allDist. The array is cut in such way that there
    ### is no empty element (1000 for path, 0 for dist). 
    ### choiceA is a 2 elements array (integer) which indicate the limit of the subarray to swap. choiceA has been previously sorted and thus, choiceA[0]
    ## has a lower value than choice[1]. 
    ### choice_B1 and choice_B2 are two integer which indicate the limit of the subarray of pathB to swap. They are not ordered, hence, choice_B2
    ### can be smaller than choice_B1. 

    ### determine lowerBound and upperbound of the subArray of pathB
    upperBoundB = int(max([choice_B1,choice_B2]))
    lowerBoundB = int(min([choice_B1,choice_B2]))

    ###we defined the subvector that will be swap (A2 and B2)
    subVectorPathA = newPathVectorA[(choiceA[0]+1):(choiceA[1])]
    subVectorPathB = newPathVectorB[(lowerBoundB+1):(upperBoundB)]

    subVectorDistA = newDistVectorA[choiceA[0]:(choiceA[1])]
    subVectorDistB = newDistVectorB[lowerBoundB:(upperBoundB)]


    ### if choice_B1 > choice_B2
    if choice_B1 > choice_B2:
        #we flip all the subvector
        subVectorPathB = np.flip(subVectorPathB)
        subVectorDistB = np.flip(subVectorDistB)
        subVectorPathA = np.flip(subVectorPathA)
        subVectorDistA = np.flip(subVectorDistA)


    ### we prevent some exception occuring when the limit of the subArray coincide with the limit of the array...
    ### we plug A2 with B1 ---> B1 A2
    ### we plug B2 with A1 ---> A1 B2
    if choiceA[0] != 0:        
        newPathVectorA_buffer = np.append(newPathVectorA[0:choiceA[0]+1],subVectorPathB)
        newDistVectorA_buffer = np.append(newDistVectorA[0:(choiceA[0])],subVectorDistB)
    else:
        newPathVectorA_buffer = np.append(newPathVectorA[0],subVectorPathB)
        newDistVectorA_buffer = subVectorDistB
           
    if lowerBoundB != 0:        
        newPathVectorB_buffer = np.append(newPathVectorB[0:lowerBoundB+1],subVectorPathA)
        newDistVectorB_buffer = np.append(newDistVectorB[0:(lowerBoundB)],subVectorDistA)
    else:
        newPathVectorB_buffer = np.append(newPathVectorB[0],subVectorPathA)
        newDistVectorB_buffer = subVectorDistA

    ### we prevent some exception occuring when the limit of the subArray coincide with the limit of the array...
    ### we plug B3 with (B1 A2) ---> (B1 A2 B3)
    ### we plug A3 with (A1 B2) ---> (A1 B2 A3)       

    if choiceA[1] != (len(newPathVectorA)-1):
            newPathVectorA = np.append(newPathVectorA_buffer,newPathVectorA[choiceA[1]:-1])
            newDistVectorA = np.append(newDistVectorA_buffer,newDistVectorA[choiceA[1]:-1])

    else :
            newPathVectorA = np.append(newPathVectorA_buffer,newPathVectorA[-1])
            newDistVectorA = newDistVectorA_buffer

    if upperBoundB != (len(newPathVectorB)-1):
            newPathVectorB = np.append(newPathVectorB_buffer,newPathVectorB[upperBoundB:-1])   
            newDistVectorB = np.append(newDistVectorB_buffer,newDistVectorB[upperBoundB:-1])

    else:
            newPathVectorB = np.append(newPathVectorB_buffer,newPathVectorB[-1])
            newDistVectorB = newDistVectorB_buffer
    

    return newPathVectorA,newDistVectorA,newPathVectorB,newDistVectorB



### FROM HERE START THE MAIN
### Free parameter
bestSolution = 350000
deathRate = 100 ### this parameter is poorly designed...
location = 119
filename = 'data.txt'
# folderpath = 'C:/Users/TEMP/Documents/apprentissage/DSTI/Class/heuristicOptimization/metrochallenge' 
folderpath = 'C:\Project\ga\ChinesePostmanProblem-master'
filename_Dic = 'stationDictionnary.txt'
mutationRatio = 0.2
numberOfEvents = 100
numberGeneration = 50
numberOfIteration = 5000
numberOfWalker = 100



#### those parameter shouldnt be touch
roamingParameter = 0.01
tabouLength = 4

###change directory
os.chdir(folderpath)

### created the mappingMetro matrix
mappingMetro = BuildMap(filename)

### find the list of all the intramuraux station
intraStation = BuildObjectiveMapHeuristicWay(filename_Dic,mappingMetro)

### get your sample of random walker
allPath,allDist = randomWalk(location, numberOfIteration, numberOfWalker, roamingParameter, tabouLength, map, intraStation, 'firstSolution')




for i in range(numberGeneration):


    title = ['generation' + str(i)]
    print(title)
    print(np.sum(allDist,axis = 1))
    print(['min Value = ' + str(np.min(np.sum(allDist,axis = 1)))])
    print(['mean Value = ' + str(np.mean(np.sum(allDist,axis = 1)))])
    print(['median Value = ' + str(np.median(np.sum(allDist,axis = 1)))])
    print(['var value =' + str(np.var(np.sum(allDist,axis = 1)))])


    allPath, allDist = generation(allPath,allDist,numberOfEvents,intraStation,deathRate,mutationRatio,mappingMetro)
    

    if (np.min(np.sum(allDist,axis = 1)) < bestSolution) and (np.min(np.sum(allDist,axis = 1)) != 0) :
        bestSolution = np.min(np.sum(allDist,axis = 1))
        bestPath = allPath[np.argmin(np.sum(allDist,axis = 1))]
        bestDist =  allDist[np.argmin(np.sum(allDist,axis = 1))]





print(bestSolution)
np.savetxt('allPathFinalSolution',bestPath , delimiter=',',fmt='%i')
np.savetxt('allDistanceFinalSolution',bestDist ,delimiter=',',fmt='%i')
np.savetxt('sumAllDistanceFinalSolution',np.sum(allDist,axis = 1),delimiter =',',fmt='%i')

print("--- %s seconds ---" % (time.time() - start_time))


 