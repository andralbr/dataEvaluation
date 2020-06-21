##############################################################################
### A class to process Matlab Log files [class LogProcessor].
### Converts Log files to a format suitable for data evaluation. 
### Overlapping processes/time stamps are merged.
###
### Log file format:
###    $Start,ProcessID,Time stamp (Y-m-d H:M)
###    $END,ProcessID,License No,Version,Time stamp (Y-m-d H:M),Toolboxes (separated by ':')
###
### Output format:
###    License, Version, Toolbox, Start timestamp, End timestamp, DeltaTime (in hours).
###
### To modify output format:
### Modify the write step in processData() - Tagged: "WRITING OUTPUT FILE".
###
### Class LogProcessor:
### -------------------
### Public methods:
###   - process(fileName, [opt.] outputFile = "outFile.txt", 
###             [opt.] outputDirectory = "./myFolder")
###     The main method to process data files. fileName can be a single
###     file or a list of files ["file1.csv", "file2.csv", ...]. If outputFile is
###     given, all outputs are appended to that file; otherwise an output file
###     p_[name] is created for each input file.
###     WARNING: The output file is always written in append mode. If a file of the
###     same name already exists, the output is appended.
###  
###   - setTimeFilter(startTime, endTime)
###     with start/end time the start and end time of the filter.
###     e.g. startTime = "16.06.2020 00:00", endTime = "17.06.2020 00:00"
###     Sets time filter. Only entries within the time range are processed
###     for the output file.
###  
###   - clearTimeFilter()
###     Delete time filter.
###
###   - setDateFormat( formatString )
###     Set format for output and filter time. 
###     Default: formatString =  "%d.%m.%Y %H:%M"
###
### Private methods:
###  - __determineValidEntries():
###    Pre-Processing method, which marks all valid lines in log file, i.e.
###    lines corresponding to processes with START and END tag.
###  - __processData():
###    Processes the data of a log file and writes output file.
###  - __processTime():
###    Associates toolboxes with time stamps.
###    (used by __processData())
###  - __mergeTimeStamps():
###    Merges overlapping time stamps of (partly) simultaneous processes.
###    (used by _processTime())
###
### 2020-06-20 Andreas Albrecht
################################################################################


import os   
from datetime import date, datetime

class LogProcessor:

    # =================
    # Constructor
    # =================
    def __init__(self):

        # Format of output date (output + filter)
        self.dateFormat = "%d.%m.%Y %H:%M"
        
        # Date/time filter 
        # (Activate/deactivate in set/clearTimeFilter())
        self.timeFilter = False
        self.filterStart = None
        self.filterEnd   = None

    # =====================
    # setTimeFilter()
    # =====================

    # Activate time filter by setting a start and end time stamp.
    # Input parameters:
    #   - filterStart: Start time, e.g. "14.06.2020 00:00".
    #   - filterEnd: End time, e.g. "15.06.2020 00:00".
    # Important: The timestamp string must be in the format defined by
    # self.dateFormat.
    #
    def setTimeFilter(self, filterStart, filterEnd):
        self.timeFilter = True
        self.filterStart = datetime.strptime(filterStart, self.dateFormat)
        self.filterEnd = datetime.strptime(filterEnd, self.dateFormat)

    # =====================
    # clearTimeFilter() 
    # =====================
    
    # Delete time filter.

    def clearTimeFilter(self):
        self.timeFilter = False
        self.filterStart = None
        self.filterEnd = None

    # =====================
    # setDateFormat()
    # =====================

    # Set format of output and filter input date format.
    # The default value (see __init__) is "%d.%m.%Y %H:%M".

    def setDateFormat(self, dateFormat):
        self.dateFormat = dateFormat


    # =======================
    # process()
    # =======================

    # The main function to process datafile(s). 
    #
    # Uses: __processData()
    #       __determineValidEntries()
    #
    # Input parameters:
    #   - files: Name of log file to be processed, e.g. "myLog.txt".
    #        Or: list of log files ["myLog1.txt", "myLog2.txt", "myLog3.txt"].
    #   - outputFile: If defined ALL (!) processed data is appended to that
    #       file. 
    #   - outputDirectory: Directory of output file(s).
    # 
    # Important:
    #   - If outputFile is not defined, an output file "p_<inputFile>" is
    #     created for each input file. 
    #     If outputFile is defined, the output of all input files is added
    #     to that file.
    #   - Output data is always appended. That is, if a file of that name
    #     already exists, its content is not overwritten. 
    #

    def process(self, files, outputFile = "", outputDirectory = "" ):
        if not isinstance(files, list):
            files = [files]
            
        for file in files:
            print("---------------------------------")
            print("Processing file " + file + "...")
            print("---------------------------------")
            
            # Determine output file name
            if outputFile:       # Output of ALL input file will be added to the same output file
                outFile = os.path.join(outputDirectory, outputFile)
            else:                # One output file for each input file is generated
                fileName = os.path.basename(file)
                outFile = os.path.join(outputDirectory, "p_" + fileName)

            validLines, numberLines = self.__determineValidEntries(file) 
            self.__processData(file, outFile, validLines, numberLines)
                
            print("Output file: " + outFile)



    # =============================
    # determineValidEntries()
    # =============================

    # Checks for valid entries in log file. Valid entries correspond to processes,
    # which have both a $START and $END entry in the log file.
    # (Processes which e.g. are not properly terminated are sorted out)
    #
    # Input paramter:
    #   fileName: Name of log file
    # Output parameters:
    #   validLines: Vector with line numbers of valid lines, e.g. [1, 2, 4, 5, 6]
    #   numberLines: The total number of lines in input log file. 

    def __determineValidEntries( self, fileName ):

        openDict = {}    # Dictionary that contains <processID, lineNumber> for a start process.
        validLines = []  # Lines numbers of valid lines in file


        with open(fileName, 'r') as readFile:
            lineNumber = 0
            for line in readFile:
                # ------------------------------------------------------------
                # START line found => add {processID: lineNumber} to openDict
                # ------------------------------------------------------------
                if line.startswith('$START'):
                    # Get process ID
                    processID = line.split(',')[1]
                    # Add {processID: lineNumber} entry to openDict
                    openDict[processID] = lineNumber

                # ------------------------------------------------------    
                # END line found:
                #     - Check if start entry for processID exists
                #     - Add line of START and END entry to 'validLines'
                #     - Delete START entry from dict openDict
                # ------------------------------------------------------
                elif line.startswith("$END"):
                    # Check if process ID for END process has a corresponding start time
                    # i.e. check if processID entry exists in openDict
                    processID = line.split(',')[1]
                    if processID in openDict:
                        validLines.append(openDict[processID])
                        validLines.append(lineNumber)
                        del openDict[processID]

                lineNumber = lineNumber + 1

        numberLines = lineNumber
        
        print("\tLines (total, valid) = " + str(lineNumber) + ", " + str(len(validLines)))
        print("\tNon-terminated processes = " + str(len(openDict))) 
        
        return validLines, numberLines


    # ==========================
    # __processData()
    # ==========================

    # Data porcessing of an input file. Combines start end times to
    # time ranges and writes output file. The actual processing function
    # for a given input file.
    #
    # Input paramters: 
    #   - inputFile: name of input file.
    #   - outputFile: name of output file
    #   - valid lines: a vector with indices of valid lines in inputFile.
    #       (output of _determineValidEntries)
    #   - numberLines: number of lines in inputFile.
    #       (output of _determineValidEntries)

    def __processData(self, inputFile, outputFile, validLines, numberLines):

        # Create a list with each entry representing a line of input file
        # and False = will not be processed, True = will be processed.
        lineValid = [False] * numberLines
        for idx in validLines:
            lineValid[idx] = True

        # Initialize variables
        noInstances = 0      # Counts how many instances are open at the same time.    
        timeMap = {}         # Map, saves {ProcessID: time}.
        timeVector = []      # Vector to capture time stamps of an instance/ process.
                             # Instance(k): start time = timeVector[2k], end time = timeVector[2k+1]
        toolboxes = []       # Vector to capture toolboxes for instance/process.
                             # Instance(k): toolboxes = toolboxes[k]

        # Variables temporarily save data for overlapping instances. Once the last of 
        # possibly several open instances is closed, the data is processed, written
        # to output file and the variables are cleared.

        with open(inputFile, 'r') as readFile:
            with open(outputFile, 'a') as writeFile:
                lineNumber = 0

                # Loop over input file lines
                for line in readFile:
                    # Only 'valid' lines are processed
                    if lineValid[lineNumber]:

                        # ------------------------------------------------------------
                        # START line found:
                        #     - add {processID: start time} to timeMap dict.
                        # ------------------------------------------------------------
                        if line.startswith('$START'):
                            line = line.rstrip('\n')  # remove \n at end of line

                            # Get process ID and time stamp
                            substr = line.split(',')  # split in substrings
                            processID = substr[1]     # get process ID
                            timeStamp = substr[2]     # get time stamp and convert to datetime format
                            timeStamp = datetime.strptime(timeStamp, "%Y-%m-%d %H:%M")

                            # Add process ID and time stamp to dict
                            timeMap[processID] = timeStamp

                            # Increase number of active instances
                            noInstances = noInstances + 1

                        # -----------------------------------------------------
                        # END line found:
                        # If the last active instance:
                        #    - Process time stamps and write output data
                        # else
                        #    - Add [start, end time] of process to timeVector
                        #    - Add toolboxes of process to toolboxes
                        #    Interpretation:
                        #    timeVector[2n], timeVector[2n+1] is the start/end time
                        #    of a process with toolboxes toolboxes[n].
                        # -----------------------------------------------------

                        elif line.startswith("$END"):

                            # Get data
                            line = line.rstrip('\n')  # remove \n at end of line
                            substr = line.split(',')  # split in substrings

                            processID = substr[1]    # Process ID
                            licenseNo = substr[2]    # License Number
                            version   = substr[3]    # Software Version
                            endTime = substr[4]      # End time of process/instance
                            endTime = datetime.strptime(endTime, "%Y-%m-%d %H:%M")
                            tbox = substr[5].strip('][').split(':')

                            # Get start time for process (from timeMap)
                            if not processID in timeMap:
                                print("ERROR: (line number = " + str(lineNumber) + ")" )
                                print("No start time found for the end timestamp.")
                                lineNumber = lineNumber + 1
                                continue
                            else:
                                startTime = timeMap[processID]

                            # Add start/end time and toolboxes    

                            # If time filter active => add only processed that fall within
                            # filter time. 
                            if self.timeFilter:
                                if startTime < self.filterEnd and endTime > self.filterStart:
                                    # Time range lies within filter time range
                                    startTime = max(startTime, self.filterStart)
                                    endTime = min(endTime, self.filterEnd) 
                                    
                                    timeVector.append(startTime)
                                    timeVector.append(endTime)
                                    toolboxes.append(tbox)
                                    
                            # No time filter active => add all times        
                            else: 
                                timeVector.append(startTime)
                                timeVector.append(endTime)

                                toolboxes.append(tbox)
                            
                            # Delete start time entry from dict
                            del timeMap[processID]

                            # One instance closed by "END" => decrease active instance counter
                            noInstances = noInstances - 1

                            # ---------------------------------------------------
                            # If last active instance: process & output data
                            # ---------------------------------------------------
                            if noInstances == 0:
                                
                                toolboxes, timeVectors = self.__processTime(timeVector, toolboxes)

                                # For all toolboxes, write the cooresponding time stamps to output
                                # file.
                                for cc in range(len(toolboxes)):
                                    toolbox = toolboxes[cc]
                                    noIntervals = int(len(timeVectors[cc])/2)

                                    for cy in range(noIntervals):
                                        startTime = timeVectors[cc][2*cy]
                                        endTime = timeVectors[cc][2*cy+1]

                                        dt = endTime - startTime
                                        dt = dt.total_seconds() / (60*60)   # time dt in hours

                                    #################################################
                                    #### WRITING OUTPUT FILE                      ###
                                    #################################################
                                        writeFile.write( licenseNo + ", "    
                                            + version + ", "
                                            + toolbox + ", "
                                            + startTime.strftime(self.dateFormat) + ", "
                                            + endTime.strftime(self.dateFormat) + ", "
                                            + '{:.2f}'.format(dt) + "\n" )

                                    #################################################
                                    
                                # Clean temporary data vector    
                                timeVector = []
                                toolboxes = []


                    lineNumber = lineNumber + 1




    ####################
    ## __processTime()
    ####################
    ##
    ## Converts a list of time stamps and associated toolboxes
    ## to a list of unique time stamps for each toolbox.
    ##
    ## Input parameters:
    ##    - timeVector: Vector of start/end times. Time stamp k
    ##        is formed by:
    ##                  start_time(k) = timeVector[2k]
    ##                  end_time(k) = timeVector[2k+1]
    ##    - toolboxes: List of toolboxes associated with a time stamp.
    ##      List of toolboxes associated with time stamp k:
    ##      toolboxes[k]
    ##
    ## Output parameters:
    ##    - uniqueToolboxes: List of unique toolbox names.
    ##    - time_list: List of start/end times vectors. 
    ##      time_list[k] is the start/end time vector for 
    ##      toolbox uniqueToolboxes[k]. A vector can consist of multiple
    ##      time stamps (multiple start/end time pairs).
    ## 
    ## Example:
    ## Input
    ##       timeVector = [datetime(2020,6,16,16,30),
    ##                     datetime(2020,6,16,16,45),
    ##                     datetime(2020,6,16,16,22),
    ##                     datetime(2020,6,16,18,5)]
    ##       toolboxes = [['matlab', 'simulink'],
    ##                    ['matlab']]
    ##
    ## Output
    ##       uniqueToolboxes = ['simulink', 'matlab']
    ##       time_list = [[datetime(2020,6,16,16,30), datetime(2020,6,16,16,45)],
    ##                    [datetime(2020,6,16,16,22), datetime(2020,6,16,18,5)]]


    def __processTime(self, timeVector, toolboxes):
        
        time_list = []
        
        # Determine unique toolbox names
        tboxesFlat = [item for sublist in toolboxes for item in sublist]
        uniqueToolboxes = list(set(tboxesFlat)) 
        
        # For each toolbox: Create an associated time stamp vector.
        for toolbox in uniqueToolboxes:
            timeTbx = []    
                
            cc = 0
            
            # Loop over all time stamps 
            # (specifically: list of toolboxes for each time stamp)
            for tbxList in toolboxes:
                # If the time stamp included the current toolbox:
                # add time stamp to toolbox time vector.
                if toolbox in tbxList:
                    timeTbx.append(timeVector[2*cc])   #start time
                    timeTbx.append(timeVector[2*cc+1]) #end time
                cc = cc + 1;
            
            # Detect and merge overlapping time stamps
            timeTbx = self.__mergeTimeStamps(timeTbx)
            
            # Add to output vector
            time_list.append(timeTbx)
            
        return uniqueToolboxes, time_list
    


    #######################
    ## mergeTimeStamps()
    #######################
    ##
    ## Detect and merge overlapping time stamps.
    ##
    ## Input:
    ##    - timeStamps: List of time stamps. Time stamp k:
    ##      start_time = timeStamps[2*k], end_time = timeStamps[2*k+1]
    ##
    ## Output:
    ##    - mergedTimeArray: List of non-overlapping time stamps.
    ##
    ## Example: 
    ##    timeStamps = [0, 4, 6, 9, 3, 7, 10, 11]
    ##    => mergedTimeArray = [0, 9, 10, 11]
    ##    (Works analogously if entries are of format datetime()).


    def __mergeTimeStamps( self, timeStamps ):
        mergedTimeArray = []   # If a non-overlapping time stamp found, it
                            # will be added to this output array.
        
        if len(timeStamps) % 2 != 0:
            print("[mergeTimeStamps] ERROR: Unexpected number of timestamp entries.")
            return
        
        noElements = int(len(timeStamps)/2)   # Total number of timestamps
        indices = range(0, noElements)        # Indices for loop over timestamps
        activeElements = [True] * noElements  # Indicates, which timestamp elements are yet unprocessed
        
        # Select first element to be processed
        element = [timeStamps[0], timeStamps[1]]
        activeElements[0] = False              
        
        # While there are still unprocessed elements in timeStamps vector
        while any(activeElements):   
            afterMerge = False 
            
            # Check timeStamp 'element' for overlap with all other (active)
            # elements of timeStamp vector.
            for n in [idx for idx in indices if activeElements[idx]]:
                
                timePair = [timeStamps[2*n], timeStamps[2*n + 1]]
                
                # If overlap found => merge time stamps
                if not (timePair[0] > element[1] or timePair[1] < element[0]):
                    element = [min(element[0], timePair[0]), max(element[1], timePair[1])]
                    activeElements[n] = False
                    afterMerge = True
                    break            # The test will start over with the new merged element
            
            # If no overlap with any other time interval found:
            # Add element to output array, and set the next unprocessed timeStamp as the
            # element to be processed.
            if not afterMerge:
                mergedTimeArray = mergedTimeArray + element
                
                idx = activeElements.index(True)
                element = [timeStamps[2*idx], timeStamps[2*idx+1]]
        
        # All elements have been processed, add last element to output array.
        mergedTimeArray = mergedTimeArray + element
        
        return mergedTimeArray