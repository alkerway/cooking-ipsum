from bs4 import BeautifulSoup
import requests
import sys

sys.stdout = open('out.log', 'w')

parentUrl = 'https://alexandracooks.com/recipe-archive'

parentText = ''
with open('archive.html', 'r') as archive:
    parentText = archive.read()

soup = BeautifulSoup(parentText, 'html5lib')

allSections = soup.findAll('ul', {'class': 'lcp_catlist'})
# .find_all('a')
recipeLinks = []
recipeTitles = []
for idx, section in enumerate(allSections):
    linkElements = section.find_all('li')
    for linkEl in linkElements:
        linkTag = linkEl.find('a', href=True)
        recipeLinks.append(linkTag['href'])
        recipeTitles.append(linkTag.getText())

for idx in range(150, len(recipeLinks)):
    sys.stdout.flush()
    print(f'processing idx {idx}')
    link = recipeLinks[idx]
    print(link)
    recipePage = requests.get(link).text
    recSoup = BeautifulSoup(recipePage, 'html5lib')
    instructionContainers = recSoup.findAll('div', {'class': 'tasty-recipes-instructions'})
    instructionContainer = instructionContainers[0] if len(instructionContainers) else None
    if len(instructionContainers) > 1:
        # print(instructionContainers)
        for i in instructionContainers:
            if i.find('p'):
                instructionContainer = i
        for i in instructionContainers:
            if i.find('ol'):
                instructionContainer = i

    ingredientsContainer = recSoup.find('div', {'class': 'tasty-recipes-ingredients'})
    if instructionContainer and ingredientsContainer:
        recipeTitle = recSoup.find('h2', {'class': 'tasty-recipes-title'}).getText()
        instructionText = ''
        instructionList = instructionContainer.find('ol')
        if instructionList:
            instructionText = instructionList.getText().strip()
        else:
            instructionText = instructionContainer.find('p', {'id': 'instruction-step-1'}).getText()
        ingredientsTextList = ingredientsContainer.find('ul')
        if ingredientsTextList:
            ingredientsText = ingredientsTextList.getText().strip()
        else:
            ingredientsPs = ingredientsContainer.findAll('p', {'class': 'p1'})
            ingredientsText = '\n'.join([i.getText() for i in ingredientsPs])
        if recipeTitle and instructionText and ingredientsText:
            with open(f'downloads/{idx}.txt', 'w') as out:
                out.write(recipeTitle)
                out.write('\n==========\n')
                out.write(ingredientsText)
                out.write('\n==========\n')
                out.write(instructionText)
            continue
    print(f'  !!!! No instructions, ingredients or title post {idx}')
    # break
sys.stdout.close()