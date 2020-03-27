import re

def split_text(text):
    
    text = text.replace('&gt;','>')
    split = text.split(' ')
    new_split = []

    for i in split:
        if i != '<a' and i != '' and 'href' not in i:
            new_split.append(i)
        
        if 'href' in i :
            start = i.find('>')
            end = i.find('<')

            if i[start+1:end] == 'PHTX':
                new_split.append(i[start+1:end])
                break

            new_split.append(i[start+1:end])

    return new_split

