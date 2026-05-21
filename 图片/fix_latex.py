from pathlib import Path
import re

base = Path(r"E:\daima\lianyu-pro\图片")
src = base / "main.tex"
dst = base / "main_fixed.tex"

text = src.read_text(encoding="utf-8")

# 常见 LaTeX 命令自动补反斜杠
commands = [
    "documentclass", "usepackage", "usetikzlibrary",
    "IfFontExistsTF", "setmainfont", "hypersetup", "graphicspath",
    "setlength", "linespread", "setcounter", "sloppy", "pagestyle",
    "fancyhf", "cfoot", "fancyhead", "renewcommand", "newcommand",
    "AtBeginDocument", "counterwithin", "DeclareCaptionFont",
    "captionsetup", "titleformat", "titlespacing", "tikzset",
    "begin", "end", "clearpage", "thispagestyle", "pagenumbering",
    "tableofcontents", "section", "subsection", "subsubsection",
    "caption", "label", "toprule", "midrule", "bottomrule",
    "endfirsthead", "endhead", "bibitem", "url",
    "noindent", "vspace", "hspace", "vfill", "par",
    "centering", "raggedright", "raggedleft", "flushright",
    "includegraphics", "IfFileExists", "fbox", "parbox", "resizebox",
    "textbf", "texttt", "makecell", "underline", "makebox",
    "zihao", "songti", "heiti", "kaishu", "rmfamily",
    "bfseries", "small", "scriptsize", "textwidth", "textheight",
    "qquad", "quad", "hfill", "square", "blacksquare",
    "item", "draw", "node"
]

# 行首命令补反斜杠
for cmd in commands:
    text = re.sub(rf"(?m)^(\s*){cmd}(\b|\[|\{{)", rf"\1\\{cmd}\2", text)

# 大括号内部常见命令补反斜杠
for cmd in [
    "thepage", "thesection", "thesubsection", "thesubsubsection",
    "arabic", "thesistitlecn", "textwidth", "textheight",
    "hspace", "makebox", "underline", "zihao", "heiti", "songti",
    "kaishu", "bfseries", "rmfamily", "small", "scriptsize",
    "centering", "par"
]:
    text = re.sub(rf"(?<!\\)\b{cmd}\b", rf"\\{cmd}", text)

# 修复 begin/end 环境
text = re.sub(r"(?<!\\)\bbegin\{", r"\\begin{", text)
text = re.sub(r"(?<!\\)\bend\{", r"\\end{", text)

# 修复表格换行：很多行本来应该以 \\ 结尾
# 对 top/mid/bottomrule 前一行不强行处理，避免误伤

# 修复 placeholder 中的 centering #1
text = text.replace(r"\centering #1", "\\centering\n      #1")

# 修复 screenshotfig 里面的宽度写法
text = text.replace("#2\\textwidth", "#2\\textwidth")
text = text.replace("0.82\\textwidth", "0.82\\textwidth")

# 修复 titleformat 里缺少反斜杠导致的组合词
text = text.replace(r"\centeringzihao", r"\centering\zihao")
text = text.replace(r"\heitibfseries", r"\heiti\bfseries")
text = text.replace(r"\songtibfseries", r"\songti\bfseries")
text = text.replace(r"\rmfamilybfseries", r"\rmfamily\bfseries")

# 修复 TikZ every node.style
text = text.replace("every node.style", "every node/.style")

# 修复 URL 文献中丢失的 https://
repls = {
    r"\url{httpsflask.palletsprojects.com}": r"\url{https://flask.palletsprojects.com}",
    r"\url{httpsflask-sqlalchemy.readthedocs.ioenstable}": r"\url{https://flask-sqlalchemy.readthedocs.io/en/stable}",
    r"\url{httpsflask-jwt-extended.readthedocs.io}": r"\url{https://flask-jwt-extended.readthedocs.io}",
    r"\url{httpsdocs.sqlalchemy.org}": r"\url{https://docs.sqlalchemy.org}",
    r"\url{httpsvuejs.org}": r"\url{https://vuejs.org}",
    r"\url{httpsrouter.vuejs.org}": r"\url{https://router.vuejs.org}",
    r"\url{httpselement-plus.org}": r"\url{https://element-plus.org}",
    r"\url{httpsecharts.apache.org}": r"\url{https://echarts.apache.org}",
    r"\url{httpswww.rfc-editor.orgrfcrfc7519}": r"\url{https://www.rfc-editor.org/rfc/rfc7519}",
    r"\url{httpsdev.mysql.comdocrefman8.4en}": r"\url{https://dev.mysql.com/doc/refman/8.4/en}",
}
for a, b in repls.items():
    text = text.replace(a, b)

# 修复明显的 bibliography 格式问题
text = text.replace("[EBOL]", "[EB/OL]")
text = text.replace("[SOL]", "[S/OL]")

# 去掉最后可能的中文注释
text = text.replace("//帮我全部检查并且改好，尽量保持原格式", "")

dst.write_text(text, encoding="utf-8")
print(f"已生成：{dst}")