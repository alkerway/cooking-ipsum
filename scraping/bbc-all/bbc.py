from bs4 import BeautifulSoup
import requests
import sys
import time

sys.stdout = open('bbc.log', 'w')

# baseUrl = 'http://beebrecipes.co.uk/chefs/'

# letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# for letter in letters:
#     print(f'processing page {letter}')
#     pageLink = baseUrl + str(letter)
#     pageText = requests.get(pageLink).text
#     pageSoup = BeautifulSoup(pageText, 'html5lib')
#     linksContainer = pageSoup.find('div', {'class': 'maxwidthx'})
#     level2 = linksContainer.findAll('div', {'class': 'r'}, recursive=False)[1]
#     level3 = level2.findAll('div', {'class': 'r'})[2]
#     links = level3.findAll('a', href=True)
#     # print(len(links))
#     for linkTag in links:
#         url = linkTag['href']
#         with open(f'chefs.txt', 'a') as out:
#             out.write('http://beebrecipes.co.uk' + url + '\n')
    # break

# chefs = []
# with open('chefs.txt', 'r') as chefList:
#     chefs = chefList.read().split('\n')

# for idx in range(215, len(chefs)):
#     chefLink = chefs[idx]
#     print(f'processing idx {idx}')
#     print(chefLink)
#     pageText = requests.get(chefLink).text
#     pageSoup = BeautifulSoup(pageText, 'html5lib')
#     linksContainer = pageSoup.find('div', {'class': 'maxwidthx'})
#     level2 = linksContainer.findAll('div', {'class': 'r'}, recursive=False)[1]
#     level3 = level2.findAll('div', {'class': 'r'})[2]
#     links = level3.findAll('a', href=True)
#     # print(len(links))
#     for linkTag in links:
#         url = linkTag['href']
#         with open(f'recipes.txt', 'a') as out:
#             out.write('http://beebrecipes.co.uk' + url + '\n')
    # break
maxRetry = 5
currentErr = 0
def getRemoteText(link):
    global currentErr
    try:
        text = requests.get(link).text
        current = 0
        return text
    except:
        currentErr = currentErr + 1
        if currentErr >= maxRetry:
            print('max retry exceeded, exitting')
            sys.exit()
        else:
            print('NETwork error, retrying in 5')
            time.sleep(5)
            return getRemoteText(link)

recipes = []
with open('recipes.txt', 'r') as recipeList:
    recipes = recipeList.read().split('\n')

for idx in range(4818, 6000):
    sys.stdout.flush()
    recipeLink = recipes[idx]
    print(f'processing idx {idx}')
    print(recipeLink)
    pageText = getRemoteText(recipeLink)
    pageSoup = BeautifulSoup(pageText, 'html5lib')
    ingredientsElements = pageSoup.findAll('li', {'class': 'recipe-ingredients__list-item'})
    instructionElements = pageSoup.findAll('p', {'class': 'recipe-method__list-item-text'})
    header = pageSoup.find('h1')
    if len(ingredientsElements) and len(instructionElements) and header:
        ingredientsText = '\n'.join(filter(lambda x: x, [i.getText().strip() for i in ingredientsElements]))
        instructionText = '\n'.join(filter(lambda x: x, [i.getText().strip() for i in instructionElements]))
        headerText = header.getText()
        if ingredientsText and instructionText and headerText:
            with open(f'bbc/{idx}.txt', 'w') as out:
                out.write(headerText)
                out.write('\n==========\n')
                out.write(ingredientsText)
                out.write('\n==========\n')
                out.write(instructionText)
            continue
    print(f'  !!!! No instructions, ingredients or title post {idx}')
    # break

sys.stdout.close()