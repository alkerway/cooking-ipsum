from bs4 import BeautifulSoup
import requests
import sys

sys.stdout = open('out.log', 'w')

# baseUrl = 'https://whiteonricecouple.com/recipes/page/'
# for pageNo in range(1, 10):
#     pageLink = baseUrl + str(pageNo)
#     pageText = requests.get(pageLink).text
#     pageSoup = BeautifulSoup(pageText, 'html5lib')
#     archiveContainer = pageSoup.find('div', {'class': 'archives'})
#     recLinks = archiveContainer.findAll('a', href=True)
#     for linkTag in recLinks:
#         url = linkTag['href']
#         with open(f'toddlinks.txt', 'a') as out:
#             out.write(url + '\n')

urls = []
with open('toddlinks.txt', 'r') as todd:
    urls = todd.read().split()

for idx in range(5, len(urls)):
    sys.stdout.flush()
    print(f'processing idx {idx}')
    link = urls[idx]
    print(link)
    recipePage = requests.get(link).text
    recSoup = BeautifulSoup(recipePage, 'html5lib')
    instructionContainer = recSoup.find('ul', {'class': 'wprm-recipe-instructions'})
    ingredientsContainer = recSoup.find('ul', {'class': 'wprm-recipe-ingredients'})
    if instructionContainer and ingredientsContainer:
        recipeTitle = recSoup.find('h2', {'class': 'wprm-recipe-name'}).getText()
        instructionText = '\n'.join(filter(lambda x: x, [i.getText().strip() for i in instructionContainer.findAll('li')]))
        ingredientsText = '\n'.join(filter(lambda x: x, [i.getText().strip() for i in ingredientsContainer.findAll('li')]))
        # instructionText = instructionContainer.getText()
        # ingredientsText = ingredientsContainer.getText()
        if recipeTitle and instructionText and ingredientsText:
            with open(f'todd/{idx}.txt', 'w') as out:
                out.write(recipeTitle)
                out.write('\n==========\n')
                out.write(ingredientsText)
                out.write('\n==========\n')
                out.write(instructionText)
            continue
    print(f'  !!!! No instructions, ingredients or title post {idx}')
    # break

sys.stdout.close()