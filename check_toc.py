import re

path = r'D:\GitHub\KurtPage\quartz\styles\custom.scss'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# html[saved-theme="dark"] → :root:root[saved-theme="dark"]
# html[saved-theme="light"] → :root:root[saved-theme="light"]
content = content.replace(
    'html[saved-theme="dark"]',
    ':root:root[saved-theme="dark"]'
)
content = content.replace(
    'html[saved-theme="light"]',
    ':root:root[saved-theme="light"]'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('DONE')
