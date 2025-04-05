import sys
import argparse
import io
import os
from io import StringIO
from conllu import parse


def argParser():
    parser = argparse.ArgumentParser(prog='Unique Token id generator',add_help=True, description='Tool to generate unique id misc parameter')
    parser.add_argument('-i','--input', nargs='+',type=str,help='specify input file/files',required=True)
    args = parser.parse_args()
    return args



def generateUniqueId(file):
    data_file = open(file, "r", encoding="utf-8")
    data_file_name = os.path.splitext(os.path.basename(str(file)))[0]
   
    file_content = data_file.read() 
    sentences = parse(file_content)
    data_file.close()
    sentenceIDBackup = 0
    for sentence in sentences:
        sentenceIDBackup += 1
        sentenceID = sentence.metadata["sent_id"]
        if sentenceID is None:
            sentenceID = "sentence_"+ sentenceIDBackup
        for token in sentence:
            tokenMisc = token["misc"]
            if token["misc"] is None:
                token["misc"] = {}
           
            token["misc"]["UniqueTokenId"] = sentenceID + "_" +(str(token["id"]) if type(token["id"]) is not tuple else (str(token["id"][0]) + "-" +str(token["id"][2])) )

    with open(file, 'w') as f:
        f.writelines([sentence.serialize() + "" for sentence in sentences])
        
if __name__ == "__main__":
    program_arguments = argParser()
    inputFiles  = program_arguments.input
    for file in inputFiles:
        generateUniqueId(file)

