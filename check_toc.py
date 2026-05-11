import re

path = r'D:\GitHub\KurtPage\quartz\styles\custom.scss'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'\n// TOC 시작 전 구분선\n\.callout \+ \.toc::before \{.*?\}\n',
    '\n',
    content,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('DONE')
