from bs4 import BeautifulSoup
import requests
import sys

sys.stdout = open('rnz.log', 'w')

# baseUrl = 'https://www.rnz.co.nz/collections/recipes?page='
# for pageNo in range(1, 126):
#     print(f'processing page {pageNo}')
#     pageLink = baseUrl + str(pageNo)
#     pageText = requests.get(pageLink).text
#     pageSoup = BeautifulSoup(pageText, 'html5lib')
#     archiveContainer = pageSoup.findAll('h3', {'class': 'o-digest__headline'})
#     for eachHead in archiveContainer:
#         linkTag = eachHead.find('a', href=True)
#         url = linkTag['href']
#         with open(f'rnzlinks.txt', 'a') as out:
#             out.write('https://www.rnz.co.nz' + url + '\n')
    # break

urls = []
with open('rnzlinks.txt', 'r') as rnz:
    urls = rnz.read().split()

for idx in range(178, len(urls)):
    sys.stdout.flush()
    print(f'processing idx {idx}')
    link = urls[idx]
    print(link)
    recipePage = requests.get(link).text
    recSoup = BeautifulSoup(recipePage, 'html5lib')
    header = recSoup.find('h1', {'class': 'c-story-header__headline'})
    recipeContainer = recSoup.find('div', {'class': 'recipe-body'})
    ingreedSection = False
    ingreeds = []
    instructSection = False
    instructs = []
    for child in recipeContainer.findChildren(recursive=False):
        if child.getText() and child.getText().strip():
            childText = child.getText().strip().encode('ascii', 'ignore').decode("utf-8")
            # print(childText)
            # print(childText.lower() == 'method')
            firstLine = childText.lower().split('\n')[0].strip()
            if firstLine == 'ingredients':
                if not len(ingreeds):
                    # print('storing ingreeds')
                    if len(childText.split('\n')) > 1:
                        ingreeds += childText.split('\n')[1:]
                    ingreedSection = True
                    continue
                else:
                    break
            if firstLine == 'method' or firstLine == 'method:':
                # print('storing method')
                if not len(instructs):
                    instructSection = True
                    if len(childText.split('\n')) > 1:
                        instructs += childText.split('\n')[1:]
                    continue
                else:
                    break
            if instructSection:
                instructs += childText.split('\n')
            elif ingreedSection:
                ingreeds += childText.split('\n')
    ingredientsText = '\n'.join(filter(lambda x: x, ingreeds))
    instructionText = '\n'.join(filter(lambda x: x, instructs))
    # print(ingredientsText, instructionText, header)
    if ingredientsText and instructionText and header:
        with open(f'rnz/{idx}.txt', 'w') as out:
            out.write(header.getText())
            out.write('\n==========\n')
            out.write(ingredientsText)
            out.write('\n==========\n')
            out.write(instructionText)
        continue
    print(f'  !!!! No instructions, ingredients or title post {idx}')
    # break

sys.stdout.close()