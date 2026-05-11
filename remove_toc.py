import os
import re

content_dir = r'D:\GitHub\KurtPage\content'

# 수동 TOC 패턴들
# 1. <strong style="color:#b3f594">Table of Contents</strong> + ul 리스트
# 2. <font color="#b3f594"><strong>Table of Contents</strong></font> + ul 리스트
# 3. %% create table of contents ... %% 주석

patterns = [
    # font 태그 방식 + 뒤따르는 ul 리스트 + 주석
    r'<font color="#b3f594"><strong>Table of Contents</strong>\s*</font>\s*\n(- \[.*?\]\(.*?\)\n)+(\t- \[.*?\]\(.*?\)\n)*',
    # strong style 방식
    r'<strong style="color:#b3f594">Table of Contents\s*</strong>\s*\n(- \[.*?\]\(.*?\)\n)+(\t- \[.*?\]\(.*?\)\n)*',
    # Obsidian 주석
    r'%%.*?table of contents.*?%%\n?',
]

def remove_manual_toc(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 주석 제거
    content = re.sub(r'%%[^\n]*table of contents[^\n]*%%\s*\n?', '', content, flags=re.IGNORECASE)
    
    # font 태그 방식 TOC 제거 (여러 줄)
    content = re.sub(
        r'<font color="#b3f594"><strong>Table of Contents</strong>\s*</font>\s*\n([ \t]*- \[.*\n)+',
        '', content, flags=re.MULTILINE
    )
    
    # strong style 방식 TOC 제거
    content = re.sub(
        r'<strong style="color:#b3f594">Table of Contents\s*</strong>\s*\n([ \t]*- \[.*\n)+',
        '', content, flags=re.MULTILINE
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'수정됨: {os.path.basename(filepath)}')
    else:
        print(f'변경없음: {os.path.basename(filepath)}')

for root, dirs, files in os.walk(content_dir):
    for fname in files:
        if fname.endswith('.md'):
            remove_manual_toc(os.path.join(root, fname))

print('완료')
