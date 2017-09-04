from bs4 import BeautifulSoup

html_doc="""
<html>
 <head>
  <title>
   The Dormouse's story
  </title>
 </head>
 <body>
  <p class="title">
   <b>
    The Dormouse's story
   </b>
  </p>
  <p class="story">
   Once upon a time there were three little sisters; and their names were
   <a class="sister" href="http://example.com/elsie" id="link1">
    Elsie
   </a>
   ,
   <a class="sister" href="http://example.com/lacie" id="link2">
    Lacie
   </a>
   and
   <a class="sister" href="http://example.com/tillie" id="link2">
    Tillie
   </a>
   ; and they lived at the bottom of a well.
  </p>
  <p class="story">
   ...
  </p>
 </body>
</html>
"""
#find 只找自己下的儿子
soup = BeautifulSoup(html_doc,features='lxml')
# tag=soup.find(name='a')
# # print(soup.prettify())
# tag.extract()
# print(tag)



# print(tag.encode())
# print(tag.decode_contents())

#find_all(name=['a','div'])

#find_all(id=['link1','link2'])

#www.cnblogs.com/wupeiqi/articles/6283017.html
#正则匹配页码
import re
re.compile('p')

# v=tag.index(tag.find('div'))
# print(v)

#查看关联标签
# soup.next_element #下一个标签
# soup.next_sibling
# tag.parents # 父级标签

#select,select_one css # 选择器
tag=soup.find(name='div')
taga=tag.find(class_='sister')
print(taga.text) #text是只读的
print(taga.string) #赋值，可设置



#append() #如果是这个HTML对象里本身就有的，那就会把这个标签从当前的位置移到了最后面。

# taga=tag.find(class_='sister')
# tag.append(taga)


#如果就是要添加 一个标签 ,如下
# obj=Tag(name='a')
# obj.string='new a'
# tag=soup.find('body')
# tag.append(obj)


#insert 必须要有索引


#创建标签之间的关系,位置不会发生变化，关系是存在的。
# tag=soup.find('div')
# a=soup.find('a')
# tag.setup(pervious_sibling=a)
# print(tag.preious_sibling)

#wrap unwrap   e.g. 如在a 标签div 包住






#



























