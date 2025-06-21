import os
import re
import requests
import hashlib
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import mimetypes

def download_and_replace_links():
    # 创建目标目录
    os.makedirs("source/images", exist_ok=True)
    
    # 缓存已下载的URL，避免重复下载
    downloaded_urls = {}
    
    # 增强版正则表达式，匹配更复杂的图片链接
    pattern = re.compile(
        r'''https?://          # http或https协议
        [^\s"\'<>()]+         # 域名部分（排除空白和特殊字符）
        \.myqcloud\.com       # 目标域名
        [^\s"\'<>()]*         # 路径部分
        /[^\s"\'<>()]+        # 文件名部分
        \.(?:jpe?g|png|webp)  # 图片扩展名
        (?:\?[^\s"\'<>()]*)?  # 可选的查询参数
        ''', re.IGNORECASE | re.VERBOSE)
    
    # 遍历themes和source目录
    for root_dir in ["themes", "source"]:
        if not os.path.exists(root_dir):
            print(f"警告: 目录 {root_dir} 不存在，跳过")
            continue
            
        for root, _, files in os.walk(root_dir):
            for file in files:
                if not should_process_file(file):
                    continue
                
                file_path = os.path.join(root, file)
                process_file(file_path, pattern, downloaded_urls)
    
    print(f"处理完成! 共替换 {len(downloaded_urls)} 个图片链接")

def should_process_file(filename):
    """检查是否为可处理的文本文件"""
    text_extensions = {'.html', '.htm', '.md', '.css', '.js', '.yml', '.yaml', '.txt', '.json', '.vue', '.jsx'}
    return os.path.splitext(filename)[1].lower() in text_extensions

def process_file(file_path, pattern, downloaded_urls):
    """处理单个文件：查找、下载并替换链接"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"无法读取文件 {file_path}: {str(e)}")
            return
    
    # 查找所有匹配的图片链接
    urls = set(pattern.findall(content))
    if not urls:
        return
    
    # 下载图片并构建替换映射
    replace_map = {}
    for url in urls:
        # 规范化URL（移除追踪参数）
        clean_url = normalize_url(url)
        if clean_url not in downloaded_urls:
            local_path = download_image(clean_url, downloaded_urls)
            if local_path:
                downloaded_urls[clean_url] = local_path
                replace_map[url] = local_path  # 原始URL可能包含额外参数
            else:
                replace_map[url] = url  # 下载失败保留原链接
        else:
            replace_map[url] = downloaded_urls[clean_url]
    
    # 替换文件中的链接
    for original_url, local_path in replace_map.items():
        # 安全替换，避免转义问题
        content = content.replace(original_url, local_path)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已更新: {file_path} ({len(urls)} 个链接)")
    except Exception as e:
        print(f"写入失败 {file_path}: {str(e)}")

def normalize_url(url):
    """规范化URL：移除无关查询参数"""
    parsed = urlparse(url)
    
    # 保留有用的查询参数（如尺寸调整）
    keep_params = {'width', 'height', 'w', 'h', 'size', 'resize'}
    query_params = parse_qsl(parsed.query)
    filtered_params = [(k, v) for k, v in query_params if k.lower() in keep_params]
    
    # 重建URL
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(filtered_params),
        ''  # 忽略fragment
    ))

def download_image(url, downloaded_urls):
    """下载图片并返回本地相对路径"""
    try:
        # 获取文件名（保留扩展名）
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        # 如果文件名没有扩展名，尝试从Content-Type获取
        if '.' not in filename:
            response = requests.head(url, timeout=5, allow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            ext = mimetypes.guess_extension(content_type) or '.bin'
            filename = f"image{ext}"
        
        # 创建安全文件名
        safe_name = re.sub(r'[^\w\-\.]', '_', filename)
        base_name, ext = os.path.splitext(safe_name)
        
        # 处理重复文件名
        local_path = f"source/images/{safe_name}"
        link_path = f"/images/{safe_name}"
        
        if os.path.exists(local_path):
            # 检查是否相同文件
            existing_size = os.path.getsize(local_path)
            response = requests.head(url, timeout=5)
            remote_size = int(response.headers.get('Content-Length', 0))
            
            if existing_size != remote_size:
                prefix = hashlib.md5(url.encode()).hexdigest()[:6]
                new_name = f"{prefix}_{base_name}{ext}"
                local_path = f"source/images/{new_name}"
                link_path = f"/images/{new_name}"
        
        # 下载图片（如果不存在或需要更新）
        if not os.path.exists(local_path):
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"下载成功: {url} -> {local_path}")
        
        return link_path
    
    except Exception as e:
        print(f"下载失败: {url} - {str(e)}")
        return None

if __name__ == "__main__":
    download_and_replace_links()