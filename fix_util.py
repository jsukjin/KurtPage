import re

path = r'D:\GitHub\KurtPage\content\Audio\SteamAudio\core\core_util.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 타겟 줄 찾기
old = 'C API Handle (`IPLContext` , `IPLScene` \ub4f1) \uc0dd\uba85\uc8fc\uae30\ub97c \uad00\ub9ac\ud558\ub294 \ud15c\ud50c\ub9bf \uc720\ud2f8\ub9ac\ud2f0 \ubaa8\uc74c'
new = 'C API Handle (`IPLContext` , `IPLScene` \ub4f1) \uc0dd\uba85\uc8fc\uae30\ub97c \uad00\ub9ac\ud558\ub294 \ud15c\ud50c\ub9bf \uc720\ud2f8\ub9ac\ud2f0 \ubaa8\uc74c ([[core_Array]] \uc5d0\uc11c \uc0ac\uc6a9\ub41c ipl \ud328\ud134\uacfc \ub3d9\uc77c)'

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('DONE')
else:
    # show what's around that section
    idx = content.find('C API Handle')
    print('NOT FOUND, context:', repr(content[idx:idx+100]))
