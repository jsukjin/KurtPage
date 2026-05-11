import re
import os

content_dir = r'D:\GitHub\KurtPage\content'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # frontmatter 끝 위치 찾기
    fm_end = content.find('\n---\n', 3)
    if fm_end == -1:
        return

    frontmatter = content[:fm_end]
    body = content[fm_end+5:]  # \n---\n 이후

    # 이미 description 있으면 스킵
    if 'description:' in frontmatter:
        return

    # 본문 맨 앞의 NOTE callout 찾기
    # > [!NOTE] \n> 내용 형식
    note_match = re.match(
        r'\s*> \[!NOTE\]\s*\n(> [^\n]*\n)+',
        body
    )
    if not note_match:
        return

    note_block = note_match.group(0)
    # callout 내용 추출 (> 제거)
    note_text = re.sub(r'^> ?', '', note_block, flags=re.MULTILINE).strip()
    # NOTE 라인 제거
    note_text = re.sub(r'\[!NOTE\]\s*\n?', '', note_text).strip()

    # frontmatter에 description 추가
    new_frontmatter = frontmatter + f'\ndescription: "{note_text}"'
    # 본문에서 NOTE callout 제거 (앞뒤 빈줄도 정리)
    new_body = body[note_match.end():].lstrip('\n')
    # 남은 --- 구분선 정리
    new_body = re.sub(r'^---\s*\n', '', new_body)

    new_content = new_frontmatter + '\n---\n' + new_body

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'수정됨: {os.path.basename(filepath)} → description: "{note_text}"')

for root, dirs, files in os.walk(content_dir):
    for fname in files:
        if fname.endswith('.md'):
            process_file(os.path.join(root, fname))

print('완료')
