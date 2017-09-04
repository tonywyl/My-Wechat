from bs4 import BeautifulSoup
html="""
<error>.......</error>
"""
def ticket():
    ret={}
    soup=BeautifulSoup(html,'html.parser')
    for tag in soup.find(name='error').find_all():
        print(tag.name,tag.text)
    return ret













