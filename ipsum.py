import random

ipPath = 'generated_recipe2.model.txt'
numLines = 6


ipLines = []
with open(ipPath, 'r') as ipFile:
    ipLines = ipFile.read().split('\n')

startIdx = random.randint(0, len(ipLines) - numLines - 1)

outputStr = ' '.join(ipLines[startIdx:(startIdx + numLines)])

print(outputStr)