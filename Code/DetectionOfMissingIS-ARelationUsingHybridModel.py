#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 07/31/2020

@author: fengbozheng
"""
######################################################################################
#Step1 Preprocessing:
######################################################################################
#pre-compute ISA removed Logical Defintion and Inherited Removed Logical Definition
import networkx as nx
file2 = open("HierarchicalRelationFile","rb")
#the content for each row: childID\tparentID\n
Dirgraph1 = nx.read_edgelist(file2, create_using = nx.DiGraph(), nodetype = str)
#
def findAncestors(node):
    Dic = dict(nx.bfs_successors(Dirgraph1,node))
    d = Dic.values()
    c = []
    for e in d:
        c = c+e
    return c  
file2.close()
allNodesInNCIt =  list(Dirgraph1.nodes)
allSubRoot = [n for n,d in Dirgraph1.out_degree() if d==0] 
#
ancestorInfo = {}
file3 = open("AncestorInformationFile","r")
#the content for each row: concept\tancestor1\tancestor2...\tancestorx\n
for lines3 in file3:
    line3 = lines3.split()
    ancestorInfo[line3[0]] = line3[1:]
file3.close()
#
import csv
conceptLexicalBOW = {}
file5 = open("BagOfWordFile","r")
#the content for each row: conceptID, bag-of-words
reader5 = csv.reader(file5)
for row5 in reader5:
    conceptLexicalBOW[row5[0]] = row5[1:]
file5.close()
#
#Stop Words:
stopWordList = ["and", "and/or", "or", "no", "not", "without", "except", "by", "after", "able", "removal", "replacement", "nos"]
stopPhraseList = [["due","to"],["secondary", "to"]]
def subList(a,b): #check if a in b
    j = 0
    for i in range(len(b)):
        if b[i:i+len(a)] == a:
            j = j+1
    if j ==0:
        return False
    else:
        return True
#generated enriched bag-of-words      
output5 = open("EnrichedBagOfWordFile_NoStopWord","w")
#the content for each row: conceptID, enriched bag-of-words
writer5 = csv.writer(output5)
for concepts in allNodesInNCIt:
    itsLexical = []
    itsLexical.append(concepts)
    itsLexical = itsLexical + conceptLexicalBOW.get(concepts)
    ancestors = ancestorInfo.get(concepts)
    for ancestor in ancestors:
        ancestorLex = conceptLexicalBOW.get(ancestor)
        if any(x in ancestorLex for x in stopWordList) == False:
            if any(subList(a,ancestorLex) for a in stopPhraseList) == False:
                for lexItem in ancestorLex:
                    if lexItem not in itsLexical:
                        itsLexical.append(lexItem)
    writer5.writerow(tuple(itsLexical))
output5.close()
#
enrichedconceptLexicalEBOW = {}
file6 = open("EnrichedBagOfWordFile_NoStopWord","r")
reader6 =csv.reader(file6)
for row6 in reader6:
    enrichedconceptLexicalEBOW[row6[0]] = row6[1:]
file6.close()
#
#Identify roots of noun chunks (R)
import spacy
nlp = spacy.load("en_core_web_lg")
file4 = open("conceptInformation1908InferredFile","r")
#the content for each row: conceptID, definition status, concept name
output4 = open("conceptNPRootFile","w")
#the content for each row: conceptID, roots of noun chunks
writer4 = csv.writer(output4)
for lines4 in file4:
    line4 = lines4.split("\n")[0].split("\t")
    conceptID = line4[0]
    conceptName = line4[2]
    doc = nlp(conceptName)
    NPRoot = []
    NPRoot.append(conceptID)
    NPRoot.append(conceptName)
    for chunk in doc.noun_chunks:
        NPRoot.append(chunk.root.text.lower())
    writer4.writerow(tuple(NPRoot))
file4.close()
output4.close()
#
conceptNPRoot = {}
file12 = open("conceptNPRootFile","r")
reader12 = csv.reader(file12)
for row12 in reader12:
    conceptNPRoot[row12[0]] = row12[2:]
file12.close()
#
#Generate enriched roots of noun chunks (ER)
output5 = open("conceptEnrichedNPRootFile","w")
#the content for each row: conceptID, enriched roots of noun chunks
writer5 = csv.writer(output5)
for concepts in allNodesInNCIt:
    itsNPRoot = []
    itsNPRoot.append(concepts)
    itsNPRoot = itsNPRoot + conceptNPRoot.get(concepts)
    ancestors = ancestorInfo.get(concepts)
    for ancestor in ancestors:
        ancestorLex = conceptLexicalSplitBySpace.get(ancestor)
        if any(x in ancestorLex for x in stopWordList) == False:
            if any(subList(a,ancestorLex) for a in stopPhraseList) == False:
                ancestorNPR = conceptNPRoot.get(ancestor)
                for lexItem in ancestorNPR:
                    if lexItem not in itsNPRoot:
                        itsNPRoot.append(lexItem)
        writer5.writerow(tuple(itsNPRoot))
output5.close()
#
enrichedNPRoot = {}
file13 = open("conceptEnrichedNPRootFile","r")
reader13 = csv.reader(file13)
for row13 in reader13:
    enrichedNPRoot[row13[0]] = row13[1:]
file13.close()
###############################################################################
#Identify associative roles 
conceptDefPlain = {}  #conceptID: list of (type, value) pairs
file7 = open("conceptRelation1908InferredFile","r")
#the content for each row: sourceID, type, destinationID
for lines7 in file7:
    line7 = lines7.split("\n")[0].split("\t")
    if conceptDefPlain.get(line7[0],"default") == "default":
        conceptDefPlain[line7[0]] = [(line7[1],line7[2])]
    else:
        conceptDefPlain[line7[0]].append((line7[1],line7[2]))
file7.close()
#
associativeRole = {}
for eachNode in allNodesInNCIt:
    originalDef = conceptDefPlain.get(eachNode,"empty")
    if originalDef != "empty":
        IsaRemovedDefinition = []
        for eachRoleRelation in originalDef:
            if eachRoleRelation[0]!= "ISA2019FZ":
                IsaRemovedDefinition.append(eachRoleRelation)
        associativeRole[eachNode] = IsaRemovedDefinition
    else:
        associativeRole[eachNode] = []
#       
output6 = open("AssociativeRoleFile","w")
for node in allNodesInNCIt:
    nodeIsaRemovedDef = associativeRole.get(node)
    if len(nodeIsaRemovedDef)>0:
        newIsaDef =[x[0]+","+x[1] for x in nodeIsaRemovedDef]
        output6.write(node+"\t"+"|".join(newIsaDef)+"\n")
    else:
        output6.write(node+"\t"+"empty"+"\n")
output6.close()
#
file8 = open("AssociativeRoleFile","r")
associativeRole = {}
for lines8 in file8:
    line8 = lines8.split("\n")[0].split("\t")
    concept = line8[0]
    if line8[1]!= "empty":
        defList = []
        conceptDefStringL = line8[1].split("|")
        for segment in conceptDefStringL:
            defList.append((segment.split(",")[0],segment.split(",")[1]))
        associativeRole[concept] = defList
    else:
        associativeRole[concept] = []
file8.close()
###############################################################################
#Step2 Logical definition comparion:
###############################################################################
#check if attributeB is more detailed than attribute A
'''
def checkSingleDetailed(attributeB,attributeA):
    if attributeB[0] == attributeA[0]:
        if attributeB[0] not in ["R135","R136","R137","R138","R139","R140","R141","R142"]:
            if (attributeA[1] in ancestorInfo.get(attributeB[1])) or (attributeB[1] == attributeA[1]):
                return True
            else:
                return False
        else:
# EXCLUDE SOMETHING, THEN IF EXCLUDE SOME SEPCIFIC THING WILL BE MORE GENERAL (less individual)
            if (attributeB[1] in ancestorInfo.get(attributeA[1])) or (attributeB[1] == attributeA[1]):
                return True
            else:
                return False
    else:
        return False
'''
def checkSingleDetailed(attributeB,attributeA):
    if attributeB[0] == attributeA[0]:
	    if (attributeA[1] in ancestorInfo.get(attributeB[1])) or (attributeB[1] == attributeA[1]):
	        return True
	    else:
	        return False
    else:
        return False
#check if group of attribute -- attributeBL is more detailed than attributeA
def checkGroupSingleDetaild(attributeBL,attributeA):
    if any(checkSingleDetailed(singleAttr,attributeA) for singleAttr in attributeBL):
        return True
    else:
        return False        
###############################################################################
#Step3 Detection of Missing IS-A relations within NLS:
###############################################################################
#Definition Status and ConCept Name
conceptInfo = {}    #conceptID: (P/D, Label)
file11 = open("conceptInformation1908InferredFile","r")
for lines11 in file11:
    line11 = lines11.split("\n")[0].split("\t")
    if conceptInfo.get(line11[0],"default") == "default":
        conceptInfo[line11[0]] = (line11[1],line11[2])
    else:
        print("error")
file11.close()
#
associationPair = {}
file12 = open("association1908InferredFile","r")
#the content for each row: conceptID1\tassociation\tconceptID2\n
for lines12 in file12:
    line12 = lines12.split()
    if associationPair.get(line12[0],"default") == "default":
        associationPair[line12[0]] = [line12[2]]
    else:
        if line12[2] not in associationPair.get(line12[0]):
            associationPair[line12[0]].append(line12[2])
    if associationPair.get(line12[2],"default") == "default":
        associationPair[line12[2]] = [line12[0]]
    else:
        if line12[0] not in associationPair.get(line12[2]):
            associationPair[line12[2]].append(line12[0])
file12.close()
#
file10= open("PrecomputedNon-latticeSubgraphsFile","r")
i = 0  #NLS sequence number
output7 = open("missingIS-AFile","w")
import csv
writer7 = csv.writer(output7)
for lines10 in file10:
    i = i+1
    print(i)
    line10 = lines10.split(";")[2]
    nodesInNLS = line10.split("|") 
    for j in range(0,(len(nodesInNLS)-1)):
        concept1DefISARemoved = associativeRole.get(nodesInNLS[j])
        concept1ShortLex = conceptLexicalBOW.get(nodesInNLS[j])
        concept1LongLex = enrichedconceptLexicalEBOW.get(nodesInNLS[j])
        concept1LongNPR = enrichedNPRoot.get(nodesInNLS[j])
        concept1ShortNPR = conceptNPRoot.get(nodesInNLS[j])
        if len(concept1DefISARemoved) >0 and any(x in concept1ShortLex for x in stopWordList) == False and any(subList(a,concept1ShortLex) for a in stopPhraseList) == False: #and len(concept1Stated)>0:
            for k in range(j+1,(len(nodesInNLS))):
                if (nodesInNLS[j] not in ancestorInfo.get(nodesInNLS[k])) and (nodesInNLS[k] not in ancestorInfo.get(nodesInNLS[j])):
                    concept2DefISARemoved = associativeRole.get(nodesInNLS[k])   
                    concept2ShortLex =  conceptLexicalBOW.get(nodesInNLS[k])
                    concept2LongLex = enrichedconceptLexicalEBOW.get(nodesInNLS[k])
                    concept2LongNPR = enrichedNPRoot.get(nodesInNLS[k])
                    concept2ShortNPR = conceptNPRoot.get(nodesInNLS[k])
                    if len(concept2DefISARemoved)>0 and any(x in concept2ShortLex for x in stopWordList) == False and any(subList(a,concept2ShortLex) for a in stopPhraseList) == False: # and len(concept2Stated)>0:
                        #NO EQUAL
                        if sorted(concept1DefISARemoved)!= sorted(concept2DefISARemoved):
                            #ISA Removed    
                            if all(checkGroupSingleDetaild(concept1DefISARemoved,Attr2) for Attr2 in concept2DefISARemoved) == True:
                                if set(concept1LongLex).issuperset(set(concept2ShortLex)):
                                    if set(concept1LongNPR).issuperset(set(concept2ShortNPR)):
                                        if nodesInNLS[k] not in associationPair.get(nodesInNLS[j],[]) and nodesInNLS[j] not in associationPair.get(nodesInNLS[k],[]):
                                            writer7.writerow((nodesInNLS[j],conceptInfo.get(nodesInNLS[j])[1],nodesInNLS[k],conceptInfo.get(nodesInNLS[k])[1],conceptInfo.get(nodesInNLS[j])[0],conceptInfo.get(nodesInNLS[k])[0],str(i)))
                            if all(checkGroupSingleDetaild(concept2DefISARemoved,Attr1) for Attr1 in concept1DefISARemoved) == True:
                                if set(concept2LongLex).issuperset(set(concept1ShortLex)):
                                    if set(concept2LongNPR).issuperset(set(concept1ShortNPR)):
                                        if nodesInNLS[k] not in associationPair.get(nodesInNLS[j],[]) and nodesInNLS[j] not in associationPair.get(nodesInNLS[k],[]):
                                            writer7.writerow((nodesInNLS[k],conceptInfo.get(nodesInNLS[k])[1],nodesInNLS[j],conceptInfo.get(nodesInNLS[j])[1],conceptInfo.get(nodesInNLS[k])[0],conceptInfo.get(nodesInNLS[j])[0],str(i)))
file10.close()
output7.close()    
#
#Redundancy Removement
#Add missing IS-A back to the hierarchy and check if there exist a path between the subconcept and the superconcept such that its lenngth is bigger than 1 (redundant)
import networkx as nx
file2 = open("HierarchicalRelationFile","rb")
Dirgraph1 = nx.read_edgelist(file2, create_using = nx.DiGraph(), nodetype = str)
file2.close()
#
file1 = open("missingIS-AFile","r") 
import csv
reader1 = csv.reader(file1)
allMissingISA = []
for row1 in reader1:
    allMissingISA.append((row1[0],row1[2]))
    Dirgraph1.add_edge(row1[0],row1[2])
file1.close()
#
nonRedundant = set()
for ISACheck in allMissingISA:
    allPaths = list(nx.all_simple_paths(Dirgraph1,ISACheck[0],ISACheck[1]))
    if any(len(x)>2 for x in allPaths) == False:
        nonRedundant.add(ISACheck)

     