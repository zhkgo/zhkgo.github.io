import os
import re

# 替换目录：请设置为你 Markdown 所在的目录
TARGET_DIR = "./source/_posts"  # 改成你真实路径

# 是否备份 .bak 文件
BACKUP = True

def fix_image_links_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找并替换以 /images/ 开头的链接
    new_content, count = re.subn(r'!\[([^\]]*)\]\(/images/([^\)]+)\)', r'![\1](images/\2)', content)

    if count > 0:
        print(f"✅ 修复 {count} 处链接：{filepath}")
        if BACKUP:
            os.rename(filepath, filepath + ".bak")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

def traverse_and_fix(root_dir):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                fix_image_links_in_file(os.path.join(root, file))

if __name__ == "__main__":
    traverse_and_fix(TARGET_DIR)
