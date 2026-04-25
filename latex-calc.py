import numpy as np
import re

def array_to_str(arr):
    def fmt(x):
        return f"{x:.0f}" if x == int(x) else f"{x}"
    return np.array2string(
        arr,
        formatter={'all': fmt},
        separator=' & ',
        prefix='',
        suffix=''
    )

def matrix_to_latex(mat):
    rows = []
    for row in mat:
        rows.append(" & ".join(map(array_to_str, row)))
    return "\\begin{bmatrix}\n" + " \\\\\n".join(rows) + "\n\\end{bmatrix}"

def latex_matrix_to_numpy(s: str):
    """
    将 LaTeX 形式的矩阵字符串转为 numpy 矩阵
    例如：
    1 & 0 & 0 \\
    0 & 0 & 1 \\
    0 & 1 & 0 \\
    """
    # 去掉末尾换行和多余空白
    s = s.strip()

    # 按行分割
    rows = s.split(r"\\")

    mat = []
    for row in rows:
        row = row.strip()
        if not row:
            continue
        # 按 & 分割并转成浮点数（或整数）
        nums = [int(x.strip()) for x in row.split('&')]
        mat.append(nums)

    return np.array(mat)


def latex_matmul_to_numpy(latex_str: str):
    """
    将 LaTeX 中的多个 bmatrix 矩阵连乘
    转换为 NumPy 矩阵并计算乘积
    """

    # 1. 提取所有 bmatrix 内容
    matrices = re.findall(
        r"\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}",
        latex_str,
        flags=re.S
    )

    if not matrices:
        raise ValueError("没有找到 bmatrix 环境")

    result = None

    # 2. 逐个解析并相乘
    for mat_str in matrices:
        rows = [
            list(map(float, row.split("&")))
            for row in mat_str.strip().split(r"\\")
            if row.strip()
        ]

        mat = np.array(rows)

        if result is None:
            result = mat
        else:
            result = result @ mat

    return result

