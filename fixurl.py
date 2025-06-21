import os
import re
import sys

def fix_image_paths():
    """在 Hexo 的 Markdown 文件中修复图片路径，添加前导斜杠"""
    # 图片扩展名列表
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
    
    # 匹配图片链接的正则表达式
    # 匹配以下格式:
    # ![alt text](path/to/image.jpg)
    # <img src="path/to/image.jpg">
    # {% asset_img image.jpg "alt" %}
    pattern = re.compile(
        r'(!\[[^\]]*\]\()(?!\/)([^\)]+?\.(?:jpe?g|png|gif|webp|svg))\)|'  # Markdown 格式
        r'(<img\s+[^>]*src=["\'])(?!\/)([^"\']+?\.(?:jpe?g|png|gif|webp|svg))|'  # HTML 格式
        r'({%\s*asset_img\s+)(?!\/)([^\s]+?\.(?:jpe?g|png|gif|webp|svg))',  # Hexo 标签
        re.IGNORECASE
    )
    
    # 计数器
    files_processed = 0
    links_fixed = 0
    
    # 遍历 source 目录
    for root, _, files in os.walk("source"):
        for file in files:
            if file.lower().endswith('.md'):
                file_path = os.path.join(root, file)
                files_processed += process_file(file_path, pattern)
                links_fixed += 1
    
    print(f"处理完成! 扫描了 {files_processed} 个 Markdown 文件，修复了 {links_fixed} 个图片链接")

def process_file(file_path, pattern):
    """处理单个 Markdown 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"无法读取文件 {file_path}: {str(e)}")
        return 0
    
    # 查找并修复图片链接
    def replace_link(match):
        # 根据匹配类型处理
        if match.group(1):  # Markdown 格式 ![alt](path)
            prefix = match.group(1)
            path = match.group(2)
            return f"{prefix}/{path})"
        
        elif match.group(3):  # HTML 格式 <img src="path">
            prefix = match.group(3)
            path = match.group(4)
            return f"{prefix}/{path}"
        
        elif match.group(5):  # Hexo 标签 {% asset_img path %}
            prefix = match.group(5)
            path = match.group(6)
            return f"{prefix}/{path}"
        
        return match.group(0)  # 未知格式，原样返回
    
    # 执行替换
    new_content, count = pattern.subn(replace_link, content)
    
    # 如果有修改，写回文件
    if count > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"已修复 {file_path}: {count} 个链接")
            return 1
        except Exception as e:
            print(f"写入失败 {file_path}: {str(e)}")
    
    return 0

if __name__ == "__main__":
    # 检查 source 目录是否存在
    if not os.path.exists("source"):
        print("错误: 未找到 source 目录")
        sys.exit(1)
    
    fix_image_paths()