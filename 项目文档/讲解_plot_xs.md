# 讲解 · `plot_xs.py` 逐行（默写块 · 学）

> 2026-10-01 Claude 重写。9/30 那一版只发在对话里，没有存到你电脑上，这份是照 `my_code\plot_xs.py`（1385 字节）重新逐行写的。
> **怎么用**：开一个新文件 `copy_plot_xs.py`，放在 `my_code` 根目录（它要 `from xslib import ...`，放别处就 import 不到），**一行一行照着手敲，别复制粘贴**。敲完按 Ctrl+F5 跑，出图之后把终端输出贴给我。
> **对拍**：出来的图和 `total_xs.png` 长得一样；终端里打印的数和原文件 `plot_xs.py` 跑出来的逐位相同。
> ⚠️ 跑之前先看第 7 段：`plt.show()` 会卡住程序，**要把图窗口关掉，后面那几行 print 才会出来。**

---

## 第 1 段 · import（第 1–4 行）

```python
from xslib import total_xs
import matplotlib.pyplot as plt
import numpy as np
import os
```

| 行 | 做什么 |
|---|---|
| `from xslib import total_xs` | 从你第 5 课写的 `xslib.py` 里拿 `total_xs` 这个函数。它负责「读一个核素、把所有叶子道加成总截面」。 |
| `import matplotlib.pyplot as plt` | 🆕 **画图库**。`as plt` 的意思是起个短名字，后面写 `plt.plot` 就不用写 `matplotlib.pyplot.plot`。`plt` 这个名字是全世界通用的写法，别改。 |
| `import numpy as np` | 老朋友，后面要用 `np.log`。 |
| `import os` | 处理文件路径用。 |

---

## 第 2 段 · 定位本文件所在的文件夹（第 6–7 行）

```python
# 路径一律从本文件自己的位置算起，不依赖启动时的工作目录。
HERE = os.path.dirname(os.path.abspath(__file__))
```

从里往外读，一共三层：

| 表达式 | 是什么 | 在你电脑上的值 |
|---|---|---|
| `__file__` | 🆕 Python 自动给的变量：**这个 .py 文件自己的路径**。前后各两个下划线 | `copy_plot_xs.py`（有时只有文件名） |
| `os.path.abspath(...)` | 补成从盘符开始的完整路径 | `E:\BNCT_GPU\my_code\copy_plot_xs.py` |
| `os.path.dirname(...)` | 去掉最后一段，只留文件夹 | `E:\BNCT_GPU\my_code` |

**为什么要这一行**：VS Code 启动程序的时候，「当前目录」可能是 `E:\BNCT_GPU`（工作区根），而不是 `my_code`。
如果后面直接写 `plt.savefig("total_xs.png")`，图会存到哪个目录，取决于你从哪儿启动的程序 —— 有时存在 `E:\BNCT_GPU\`，有时存在 `my_code\`。
用 `HERE` 拼路径，图永远落在这个 .py 文件旁边。

---

## 第 3 段 · 读两个核素（第 9–11 行）

```python
T="294K"
E_b, tot_b, at_b, i0_b,awr_b = total_xs("B10", T)
E_h, tot_h, at_h, i0_h ,aer_h= total_xs("H1",  T)
```

`total_xs` 返回 **5 个东西**（看 `xslib.py` 最后那行 `return E, total, at_i0, i0, awr`），左边就要用 5 个名字一一接住。这叫**拆包**：个数必须对上，少一个会报 `ValueError: too many values to unpack`。

| 名字 | 是什么 | B-10 的实际值 |
|---|---|---|
| `E_b` | 能量网格（numpy 数组） | 941 个点，从 1e-5 到 2e7 eV |
| `tot_b` | 总截面，和 `E_b` 一一对应 | 941 个数 |
| `at_b` | 字典：MT 号 → 那个道在热能点的截面（冗余道也记） | 例：`at_b[107]` = (n,α) 总和 |
| `i0_b` | 热能点的下标：`E[i0] ≤ 0.0253 < E[i0+1]` | 242（`E[242]` = 0.024638 eV） |
| `awr_b` | 靶核质量 / 中子质量 | 9.926921 |

后缀 `_b` 表示 B-10，`_h` 表示 H-1。

> ⚠️ 第 11 行最后一个名字是 **`aer_h`**，不是 `awr_h`，是当时的笔误。它后面从来没用到，所以不会出错。
> 抄的时候改不改由你定。改了的话，逐行对照时这一行会和原文件不一样，你自己知道原因就行。

---

## 第 4 段 · 斜率判据：B-10 在热能区是不是 1/v（第 13–16 行）

```python
k = i0_b
p = np.log(tot_b[k+1]/tot_b[k]) / np.log(E_b[k+1]/E_b[k])
print("B-10 热能区 log-log 斜率 p = %.6f" % p)
assert abs(p + 0.5) < 1e-2, "p = %.6f，不是 -1/2" % p
```

**公式的来历**：假设截面在一小段里是幂律，`σ = C·E^p`。两边取对数：

```
ln σ = ln C + p·ln E
```

这是一条直线，横轴 `ln E`，纵轴 `ln σ`，**斜率就是 p**。用两个点算斜率：

```
p = (ln σ₂ − ln σ₁) / (ln E₂ − ln E₁) = ln(σ₂/σ₁) / ln(E₂/E₁)
```

代码里的 `np.log(tot_b[k+1]/tot_b[k]) / np.log(E_b[k+1]/E_b[k])` 就是这一行，`ln a − ln b = ln(a/b)`。

**为什么应该是 −1/2**：1/v 律的意思是 `σ ∝ 1/v`，而 `v ∝ √E`，所以 `σ ∝ E^(−1/2)`，p = −0.5。
B-10 的 (n,α) 在热区几乎就是严格的 1/v，你白板题⑥ 实测过 p = −0.500056。

**`assert abs(p + 0.5) < 1e-2`**：`p + 0.5` 就是 p 和 −0.5 的差。差的绝对值小于 0.01 就通过。

**`%.6f`**：格式符，意思是「小数，保留 6 位」。`%` 后面跟要填进去的值。

---

## 第 5 段 · 画两条线（第 18–19 行）

```python
plt.plot(E_b, tot_b, label="B-10")        # 第一个参数是横轴，第二个是纵轴
plt.plot(E_h, tot_h, label="H-1")
```

`plt.plot(x, y)` 会把 `(x[0], y[0])`、`(x[1], y[1])` …… 这些点用线段连起来。两个数组**长度必须一样**（B-10 是 941 对 941）。
`label=` 是这条线在图例里显示的名字，这时候还不会显示，要等第 6 段的 `plt.legend()`。

调用两次 `plt.plot`，两条线就画在**同一张图**上。

---

## 第 6 段 · 坐标轴和装饰（第 21–26 行）

```python
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Energy (eV)")
plt.ylabel("Total cross section (barn)")
plt.legend()
plt.grid(True, which="both", alpha=0.3)   # which="both" 连次刻度线也画，对数图上有用
```

| 行 | 做什么 | 为什么 |
|---|---|---|
| `xscale("log")` | 横轴改成对数刻度 | 能量从 1e-5 到 2e7，跨 12 个数量级，线性刻度下 99.99% 的点会挤在最左边 |
| `yscale("log")` | 纵轴改成对数刻度 | 截面从不到 1 barn（H-1 在 MeV 区）到约 20 万 barn（B-10 在 1e-5 eV）。**两轴都取对数以后，幂律 `σ ∝ E^p` 会变成直线**（第 4 段推过），1/v 区就是一条斜率 −1/2 的直线 |
| `xlabel` / `ylabel` | 轴标题 | 用英文，是因为 matplotlib 默认字体显示不了中文（会变成方框） |
| `legend()` | 把第 5 段的 `label` 画成图例 | 没有这一行，`label=` 写了也不显示 |
| `grid(True, which="both", alpha=0.3)` | 画网格线 | `which="both"` 指主刻度（10、100）和次刻度（20、30……）的线都画。`alpha` 是不透明度，0 是完全透明，1 是完全不透明，0.3 就是淡淡的 |

---

## 第 7 段 · 存图、显示（第 28–29 行）

```python
plt.savefig(os.path.join(HERE, "total_xs.png"), dpi=150)
plt.show()
```

| 行 | 做什么 |
|---|---|
| `os.path.join(HERE, "total_xs.png")` | 拼路径，得到 `E:\BNCT_GPU\my_code\total_xs.png`。用 `join` 不用字符串加号，是因为它会自动放对分隔符 `\` |
| `savefig(..., dpi=150)` | 存成 PNG。`dpi` 是每英寸多少像素，150 够看，300 适合打印 |
| `plt.show()` | 弹出一个窗口显示这张图 |

🔴 **两个坑**：
1. **`savefig` 必须写在 `show` 前面。** 关掉窗口以后，图就被清空了，这时候再 `savefig` 存出来的是一张白图。
2. **`show()` 会让程序停在这一行，一直到你关掉窗口。** 第 8 段那些 print 要等窗口关了才会出现。你看到终端「没动静」，不是死了，是在等你关窗口。

> 抄的时候文件名要不要改成 `copy_total_xs.png`，免得覆盖原来那张图？两张内容一样，覆盖了也没关系，你定。

---

## 第 8 段 · 把算斜率用的四个数打出来（第 31–40 行）

```python
k = i0_b
print("E[k]     = %.6e" % E_b[k])
print("E[k+1]   = %.6e" % E_b[k+1])
print("tot[k]   = %.6f" % tot_b[k])
print("tot[k+1] = %.6f" % tot_b[k+1])
print("分子 log(tot比) = %.6e" % np.log(tot_b[k+1]/tot_b[k]))
print("分母 log(E比)   = %.6e" % np.log(E_b[k+1]/E_b[k]))

print("tot_h[0]    = %.4f barn   (E=%.3e eV)" % (tot_h[0], E_h[0]))
print("tot_h[i0_h] = %.4f barn   (E=%.3e eV)" % (tot_h[i0_h], E_h[i0_h]))
```

- 前六行：把第 4 段那条斜率公式的**分子、分母和四个原料**一个个打出来，自己可以拿计算器核一遍 p。
- **`%.6e`**：科学计数法，保留 6 位小数，例：`2.463750e-02`。适合很大或很小的数。
- 最后两行：H-1 在表下限 1e-5 eV 和在热能点的总截面。你 9/18 记过：**1177.2619** 和 **30.6492**，跑出来应该是这两个数。
- 最后两行一个 `%` 后面要填**两个**值，所以必须用括号包成一组：`% (a, b)`。漏了括号是你的高频错（「% 没把多个值包成一组」3 次）。

---

## 抄完自查（不计分）

1. 拆包左边是不是 5 个名字？
2. `savefig` 是不是在 `show` 前面？
3. 最后两行 `%` 后面是不是带括号？
4. 跑出来的 p 是不是和原文件逐位相同？H-1 那两个数是不是 1177.2619 和 30.6492？
