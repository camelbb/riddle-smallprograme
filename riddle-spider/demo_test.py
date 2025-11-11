import re
from bs4 import BeautifulSoup

def extract_answers_from_html(html):
    """
    完整处理流程：使用BeautifulSoup定位元素，正则提取谜底
    """
    soup = BeautifulSoup(html, 'html.parser')
    answers = []
    
    # 查找所有包含onclick属性的input按钮
    buttons = soup.find_all('input', attrs={'onclick': True})
    
    for button in buttons:
        onclick = button['onclick']
        match = re.search(r"谜底：([^'\)\"]+)", onclick)
        if match:
            answers.append(match.group(1))
    
    return answers

# 使用示例
html_content = """
<table>
    <tr>
        <td align="right">
            <INPUT onClick="MM_popupMsg('谜底：玉米')" type=button value=查看谜底>
        </td>
    </tr>
    <tr>
        <td align="right">
            <INPUT onClick="MM_popupMsg('谜底：西瓜')" type=button value=查看谜底>
        </td>
    </tr>
</table>
"""

answers = extract_answers_from_html(html_content)
print(f"提取的所有谜底: {answers}")  # 输出: ['玉米', '西瓜']