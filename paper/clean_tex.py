import re

def batch_clean_latex(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 去除加粗星号：将 **文字** 替换为 文字
    # 逻辑：匹配两个星号开始，中间非星号内容，两个星号结束
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', content)

    # 2. 去除误转义的星号：将 \* 替换为 *
    # 很多导出工具会把普通的星号转义成 \*导致编译出错
    cleaned = cleaned.replace(r'\*', '*')

    # 3. 处理数学公式中被误加的空格星号（可选）
    # 例如将 $w * $ 修复为 $w^*$
    cleaned = re.sub(r'\s\*\s(?=\$)', r'^*', cleaned)

    # 4. 特殊保护：确保 \omega^* 这种格式不被破坏
    # 如果你的文档里有大量的 \omega* 这种漏了上标号的，可以统一修复
    # cleaned = re.sub(r'(\\omega)\*', r'\1^*', cleaned)

    # 5. 删除行首或行尾多余的修饰性星号（如果存在）
    cleaned = re.sub(r'^\s*\*\s+', '', cleaned, flags=re.MULTILINE)

    with open(file_path + '_cleaned.tex', 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    print(f"处理完成！已生成备份文件：{file_path}_cleaned.tex")

# 调用脚本（请确保文件名正确）
batch_clean_latex('paper.tex')