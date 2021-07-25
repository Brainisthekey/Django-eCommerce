


ordered_items = [['1', 'fdsfsd'], ['32', 'dsada']]
string_filed = ''
for i, item in enumerate(ordered_items):
    fstring = f'{i}. {item[0]} x {item[1]} \n'
    string_filed += fstring
b = string_filed.rstrip()
print(b)