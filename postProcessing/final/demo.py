# Import log file processing class
from LogProcessor import *


###############################
# Create instance LogProcessor
###############################
logProcessor = LogProcessor()

# Public class methods:
# - .process(fileName, [opt.] outputFile = "outFile.txt", 
#           [opt.] outputDirectory = "./myFolder")
#   The main method to process data files. fileName can be a single
#   file or a list of files ["file1.csv", "file2.csv", ...]. If outputFile is
#   given, all outputs are appended to that file; otherwise an output file
#   p_[name] is created for each input file.
#   WARNING: The output file is always written in append mode. If a file of the
#   same name already exists, the output is appended.
#
# - .setTimeFilter(startTime, endTime)
#   with start/end time the start and end time of the filter.
#   e.g. startTime = "16.06.2020 00:00", endTime = "17.06.2020 00:00"
#   Sets time filter. Only entries within the time range are processed
#   for the output file.
#
# - .clearTimeFilter()
#   Delete time filter.
#
# - setDateFormat( formatString )
#   Set format for output and filter time. 
#   Default: formatString =  "%d.%m.%Y %H:%M"



########################
# Process data files
########################

print("Examples:")

# ------------------------
# Example 1 - Single file
# ------------------------
# Creates an output file "p_[fileName]" in the current directory.

logProcessor.process("./testData/data1.csv")

# -------------------------------------------------------
# Example 2 - Multiple files and define output directory
# -------------------------------------------------------
files = ["./testData/data1.csv", "./testData/data2.csv"]
logProcessor.process(files, outputDirectory = "./out_v2")

# ---------------------------------------------------
# Example 3 - All files in folder & output directory
# ---------------------------------------------------
# All files with ending .csv in path
path = "./testData"
allFiles = [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.csv')]

logProcessor.process(allFiles, outputDirectory = "./out_v3")

# --------------------------------------------------------
# Example 4 - All files in folder & output to a single file
# --------------------------------------------------------
# All files with ending .csv in path
path = "./testData"
allFiles = [f for f in os.listdir(path) if f.endswith('.csv')]

logProcessor.process(files, outputFile = "allTogether.csv")



#####################
# Apply time filter
#####################

# Apply time filter
logProcessor.setTimeFilter("14.06.2020 00:00", "15.06.2020 00:00")

# Process data
path = "./testData"
allFiles = [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.csv')]

logProcessor.process(allFiles, outputDirectory = "./out_v4")

# Clear time filter
logProcessor.clearTimeFilter()