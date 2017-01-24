import json
import io
import Label
jsonDataSwapped = dict()
#metadataPath = "../../ILSVRC2012_metadata.json"
metadataPath = "../../ILSVRC2012_metadata.json"
with io.open(metadataPath) as metadataFile:
	#jsonFile = json.open(metadataFile)
	#jsonString = jsonFile.read()
	jsonData = json.load(metadataFile)
	jsonDataSwapped = dict((v,k) for k,v in jsonData.iteritems())
	metadataFile.close()

for lb in Label.Label:
	label = Label.Label[lb]
	if not label in jsonDataSwapped:
		print(label + " " + str(lb))

print(len(jsonDataSwapped.keys()))