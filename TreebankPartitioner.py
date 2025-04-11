import sys
from conllu import parse
import argparse
import os
import re
import random

#globals
train = sentences = parse("")
dev = parse("")
test = parse("")
partition = (0,0,0)
sentIdDefs = {}
countMWHead = False
shuffle=False

# function to count tokens or syntactic tokens in sentence
def countSynTokenInSentence(sentence):
    count = 0
    if countMWHead:
       count = len(sentence)
    else:
        for token in sentence:
            if  type(token["id"]) is not tuple:
                count += 1

    return count


def analizeConlluFile(file):

    data_file = open(file, "r", encoding="utf-8") # apri il file in lettura
    data_file_name = os.path.splitext(os.path.basename(str(file)))[0]
   
    file_content = data_file.read() # leggi il file e metti nella variabile file_content
    sentences = parse(file_content)

    if shuffle:
        print("shuffle sentences")
        random.shuffle(sentences)
        random.shuffle(sentences)

    # get total numeber of tokens
    totalToken = 0 
    for index,sentence in enumerate(sentences):
        totalToken += countSynTokenInSentence(sentence)

    fname  = ""    
    if ("_" in data_file_name):
       fname = data_file_name.split("_",1)[1].replace("_"," ")
    else:
        fname = data_file_name

    print("The distribution of the " + fname + " (tokens: "+str(totalToken)+")" + " with respect to the subsets is as follows:")

    # start-end sent_id initialization
    trainSentIdStartEnd = ["",""] 
    devSentIdStartEnd = ["",""]
    testSentIdStartEnd = ["",""]
    
    # get partition number in tokens
    trainTokenNumber = int(( totalToken * partition[0] ) / 100)
    devTokenNumber = int(( totalToken * partition[1] ) / 100)
    testTokenNumber = int(( totalToken * partition[2] ) / 100)

    sentencesInTrain= sentencesInDev= sentencesInTest = 0
    tokensInTrain= tokensInDev= tokensInTest = 0
    
    
    for index,sentence in enumerate(sentences): # for each sentece of conllu file

        # remove extra metadata tags
        if "newpar" in sentence.metadata:
            del sentence.metadata["newpar"]
        if "newdoc" in sentence.metadata:
            del sentence.metadata["newdoc"]

        # use sentence definition to compile sent_id tag... if present
        if data_file_name in sentIdDefs:
            sentence.metadata["sent_id"] = sentIdDefs[data_file_name] + str((index+1))

        # get sentence lenght
        sentenceLen = countSynTokenInSentence(sentence)

        # if the number of tokens in partition is > 0 enter in branch 
        #   append sentece to the corresponding partition
        #   increment sentence number of the corresponding partition
        #   update star-end sent_id for each partition
        if (trainTokenNumber > 0):
            train.append(sentence)
            trainTokenNumber -= sentenceLen
            sentencesInTrain += 1
            tokensInTrain += sentenceLen
            
            if len(trainSentIdStartEnd[0]) == 0:
                trainSentIdStartEnd[0] = sentence.metadata["sent_id"]
            trainSentIdStartEnd[1] = sentence.metadata["sent_id"]

        elif (devTokenNumber > 0):
            dev.append(sentence)
            devTokenNumber -= sentenceLen
            sentencesInDev +=1
            tokensInDev += sentenceLen

            if len(devSentIdStartEnd[0]) == 0:
                devSentIdStartEnd[0] = sentence.metadata["sent_id"]
            devSentIdStartEnd[1] = sentence.metadata["sent_id"]
        else:
            test.append(sentence)
            testTokenNumber -= sentenceLen
            sentencesInTest += 1 
            tokensInTest += sentenceLen

            if len(testSentIdStartEnd[0]) == 0:
                testSentIdStartEnd[0] = sentence.metadata["sent_id"]
            testSentIdStartEnd[1] = sentence.metadata["sent_id"]
    
    print ("* `train`: " +str(sentencesInTrain) +" sentences ("+ trainSentIdStartEnd[0] +"; "+trainSentIdStartEnd[1]+") - "+ str(tokensInTrain) +" tokens")
    print ("* `dev`: "+ str(sentencesInDev)+ " sentences ("+ devSentIdStartEnd[0] +"; "+devSentIdStartEnd[1]+") - "+ str(tokensInDev) +" tokens")
    print ("* `test`: "+ str(sentencesInTest)+ " sentences ("+ testSentIdStartEnd[0] +"; "+testSentIdStartEnd[1]+") - "+ str(tokensInTest) +" tokens")
    print("\n")

    data_file.close()

def main():
    global partition
    # Instantiate the parser
    parser = argparse.ArgumentParser(prog='Treebank Partitioner',add_help=True, description='Tool to partion a conllu file in train/dev/test')
    parser.add_argument('-i','--input', nargs='+',type=str,help='specify input file/files',required=True)
    parser.add_argument('-tn','--treebank_name',type=str,help='specify treebank name',default="")
    parser.add_argument('-wh','--withMultiwordHead', default=False, help='includes multiword head in the token count', action='store_true')
    parser.add_argument('-sh','--shuffleSentences', default=False, help='pre-shuffle sentences', action='store_true')
    parser.add_argument('-sd','--sent_id_def', nargs='+',type=str,help='sent_id_definition prefix for each file')
    parser.add_argument('-p','--partition',type=str,help='[default 80/10/10] Partition specification i.e. 70/20/10',default="80/10/10")
    args = parser.parse_args()


    # analyze arguments
    r = re.compile('^[0-9]*/[0-9]*/[0-9]*$')
    if r.match(args.partition) is not None:
        partition = (int(args.partition.split("/")[0]),int(args.partition.split("/")[1]),int(args.partition.split("/")[2]))
        if ((partition[0] + partition[1] + partition[2]) != 100 ):
            print("Wrong partition !! Sum of parttion is not 100, use something like 80/10/10", file=sys.stderr)
            sys.exit(1)
    else:
        print("Wrong partition !! use something like 80/10/10", file=sys.stderr)
        sys.exit(1)

    
    if (args.sent_id_def != None):
        if (len(args.sent_id_def) >  0):
            for sentDef in args.sent_id_def:
                r = re.compile('^.*=.*$')
                if r.match(sentDef) is not None:
                    definition = sentDef.split("=")[0]
                    sentIdVal = sentDef.split("=")[1]
                    definition = os.path.splitext(definition)[0]
                    sentIdDefs[definition] = sentIdVal
                else:
                    print("Wrong sent_id definition in " + sentDef + " !! use something like <fileName>=<prefixOfSentid>  i.e filenamexyz=my_sent_id_prefix_", file=sys.stderr)
                    sys.exit(1)

    return args


if __name__ == "__main__":
    program_arguments = main()
    inputFiles  = program_arguments.input
    countMWHead = program_arguments.withMultiwordHead
    shuffle = program_arguments.shuffleSentences
    for file in inputFiles:
        analizeConlluFile(file)

    print(program_arguments)
    
    with open(program_arguments.treebank_name+'-train.conllu', 'w') as f:
        f.writelines([sentence.serialize() + "" for sentence in train])
    with open(program_arguments.treebank_name+'-dev.conllu', 'w') as f:
        f.writelines([sentence.serialize() + "" for sentence in dev])
    with open(program_arguments.treebank_name+'-test.conllu', 'w') as f:
        f.writelines([sentence.serialize() + "" for sentence in test])
    
    