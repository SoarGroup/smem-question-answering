import os
import re

smemData = {}
currMicrotheory = ""

#---READING---

#Starts looking through all the files in the current directory
#	(Ignores this python file)
path = os.getcwd()
for filename in os.listdir(path):
	if (filename == "SOAR_converter.py"):
		continue

	#Resets the microtheory when it opens a new file
	currMicrotheory = ""

	f = open(filename, 'r')
	for line in f:
		#Skips current line if it isn't a rule/is too complicated (like a function)
		if (line[0] != "(" or line == "\n"):
			continue

		#TEMPORARY:
		#Skips current line if it has more than one level of enclosed parantheses
		if (line.count("(") > 1):
			continue

		line = line[:-1] #Removes the '\n' character

		#Skips over comments
		if line.find(';') > 0:
			line = line[:line.index(';')]

		#Removes the pair of parentheses at the ends of the statement
		line = line[1: line.rfind(')')]

		#Takes the first word and skips the current line if it is a comment
		tempIndex = line.find(' ')
		attr = line[0: tempIndex]
		if attr == "comment":
			continue

		#Stores the rest of the words in a list to be sorted later
		line = line[tempIndex + 1:]
		nodeAndLabels = []
		while len(line) > 0:
			label = ""
			#If the word is a set of words in a pair of quotes, do the following
			if line[0] == '"':
				tempIndex = line.find('"', 1) + 1
				label = line[1: tempIndex - 1].replace(" ", "")
				line = line[tempIndex + 1:]
			#Else if this is the last word on the line, do the following
			elif line.find(" ") == -1:
				label = line
				line = ""
			#Else do the default action
			else:
				tempIndex = line.find(" ")
				label = line[0: tempIndex]
				line = line[tempIndex + 1:]

			#Some symbols don't work with SOAR syntax
			label = re.sub('[^0-9a-zA-Z]', '', label)
			nodeAndLabels.append(label)

		#---SORTING---

		#Check if statement is about microtheory.
		#If so, record it and move to the next line.
		if attr == "in-microtheory":
			currMicrotheory = nodeAndLabels[0]
			continue

		nodeID = nodeAndLabels[0]

		#If the node is not in the dictionary,
		#	instantiate it and its list.
		if smemData.get(nodeID) == None:
			smemData[nodeID] = []
		#Add attr as a tuple of a string and an empty list for the labels
		smemData[nodeID].append((attr, []))

		#Go through the list and add labels to the tuple_list node->attr
		#(Skips over the first element, which is the node)
		iterList=iter(nodeAndLabels)
		next(iterList)
		for label in iterList:
			smemData[nodeID][len(smemData[nodeID]) - 1][1].append(label)

		#Add microtheory to node's dictionary
		if len(currMicrotheory) > 0:
			smemData[nodeID].append(("in-microtheory", [currMicrotheory]))


#---TRANSLATING---

#Once all the files have been processed, write the data to a SOAR file.
f = open("SMEM.soar", "w")
f.write("smem --add {\n")

#Iterate through every node in the smemData dictionary
for nodeKey in smemData:
	f.write("	(<" + nodeKey + "> ^krfID " + nodeKey + ")\n")
	for pair in smemData[nodeKey]:
		output = "	(<" + nodeKey + ">"
		count = 0
		for label in pair[1]:
			if count > 0:
				output += " ^nextArg " + label #do this if there is >1 label
			else:
				output += " ^" + pair[0] + " " + label
			count += 1
		output += ")\n"
		f.write(output)

f.write("}")

f.close()
