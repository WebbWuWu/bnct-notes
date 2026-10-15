# 讲解 · `total_xs` 逐行（默写块 · 学）

> 2026-10-14 Claude 写，照 `my_code\xslib.py`（9/15 写，9/21 以后没动过）逐行讲。原文件注释很长，这里剥掉注释只留能跑的行，注释里的道理并进讲解。
> **怎么用（先抄后默的「抄」）**：
> 1. 在 `my_code` 根目录新建 `copy_total_xs.py`（和 `copy_plot_xs.py`、`copy_xs_lookup.py` 放一起；必须在根目录，因为最后要 `from xslib import ...`）。
> 2. 照第 0 节**一行一行手敲**，assert 也抄（学的阶段认真看它抓什么；默写时不写）。
> 3. 文件最后粘上第 7 节的对拍块（Claude 写的，粘贴即可），Ctrl+F5。
> 4. 打印出两行「逐位相同 ✓」就算学完。
>
> **默写**：10/15（1）、10/18（2）。默的范围：import、两个常量、整个函数；**assert、print 不默**。
> 用时约 25 min。

---

## 0. 全文（照这个抄）

```python
import os
import h5py
import numpy as np

LIB    = r"E:\BNCT_GPU\lib80x_hdf5"
T      = "294K"
E_TEST = 0.0253


def total_xs(nuc, T):
    path = os.path.join(LIB, nuc + ".h5")
    assert os.path.exists(path), "文件不在这里：%s" % path

    with h5py.File(path, "r") as f:
        root  = f[nuc]
        E     = root["energy"][T][:]
        awr   = float(root.attrs["atomic_weight_ratio"])
        names = list(root["reactions"].keys())

        total = np.zeros(len(E))
        at_i0 = {}
        i0 = int(np.searchsorted(E, E_TEST, side="right")) - 1
        n_add = 0

        for name in sorted(names):
            rx = root["reactions"][name]

            mt        = rx.attrs["mt"]
            redundant = rx.attrs["redundant"]

            xs_ds = rx[T]["xs"]
            thr   = int(xs_ds.attrs["threshold_idx"])
            xs    = xs_ds[:]

            assert len(xs) + thr == len(E), \
                "%s: len(xs)=%d, thr=%d, len(E)=%d —— 对不上" \
                % (name, len(xs), thr, len(E))

            at_i0[int(mt)] = 0.0 if i0 < thr else xs[i0 - thr]

            if redundant:
                continue

            assert at_i0[int(mt)] < 1e6, \
                "%s (MT=%d) 在热能点是 %.3e barn —— 这不可能是截面，" \
                "检查 redundant 标志" % (name, mt, at_i0[int(mt)])

            total[thr:] += xs
            n_add += 1

    print("[%s] %d 个道，加了 %d 个，跳过 %d 个冗余道"
          % (nuc, len(names), n_add, len(names) - n_add))

    assert np.all(total > 0), "总截面出现非正值，最小 %.3e" % np.min(total)

    return E, total, at_i0, i0, awr
```

原文件里还有一个 `NUC = "B10"` 常量，只给 `__main__` 用，函数里用不到，抄写稿不抄。

---

## 1. 这个函数在整条链里的位置

| 谁调它 | 拿它干什么 |
|---|---|
| `plot_xs.py` / `copy_plot_xs.py` | 画 B10、H1 的总截面曲线（`total_xs.png`） |
| `lesson05_tissue_scaffold.py` | 第 5 课：软组织每个核素的总截面 × 数密度，加成宏观截面 |
| `lesson06_continuous.py` 判据 B | 和 `xs_lookup.sigma_at` 在 0.0246 eV 对拍（两条独立的路） |

**它和你熟的 `xs_lookup.load_nuclide` 有什么不同**：

```
load_nuclide  —— 每个道单独留着（mts、XS 两个列表一一对应）→ 输运时要按道抽反应
total_xs      —— 把所有不冗余的道【加成一条】total               → 只要总截面时（画图、Σt）
```

两个函数开头读文件那几行几乎一样，**不同在循环里：一个 `append` 进列表，一个 `+=` 进同一个数组**。

---

## 2. import 和三个常量

| 行 | 做什么 |
|---|---|
| `import os` | `os.path.join`、`os.path.exists` |
| `import h5py` | 读 `.h5` 截面库 |
| `import numpy as np` | `np.zeros`、`np.searchsorted`、`np.all`、`np.min` |
| `LIB = r"E:\..."` | 库的文件夹。`r` 让反斜杠不被当成转义（`\b` 本来是退格符） |
| `T = "294K"` | 温度标签。⚠️ 函数参数也叫 `T`，函数里用的是**参数**那个 |
| `E_TEST = 0.0253` | 热能点，eV。🔴 函数里算 `i0` 用的是这个**全局常量**，不是参数 |

最后那一条是这个函数的一个毛病：它有一个「藏起来的输入」。调用 `total_xs("H1", "294K")` 看不出它还依赖 `E_TEST`，改了 `E_TEST`，`i0` 和 `at_i0` 就跟着变。**只记住、不改**（`plot_xs` 等三个地方在用）。

---

## 3. 打开文件、读四样东西（和 `load_nuclide` 一样）

```python
    path = os.path.join(LIB, nuc + ".h5")
    ...
    with h5py.File(path, "r") as f:
        root  = f[nuc]
        E     = root["energy"][T][:]
        awr   = float(root.attrs["atomic_weight_ratio"])
        names = list(root["reactions"].keys())
```

| 行 | 得到什么 |
|---|---|
| `nuc + ".h5"` | `"B10"` → `"B10.h5"`：库里一个核素一个文件 |
| `f[nuc]` | 文件里最顶上那一组，名字就叫核素名 |
| `root["energy"][T][:]` | 294K 那张能量网格，`[:]` 把 HDF5 里的数据真正读成 numpy 数组 |
| `root.attrs[...]` | 🔴 `.attrs` 是 h5py 文件里的**属性**（不是 Python 字典的 `["键"]`，这对你混过） |
| `list(...keys())` | 所有道的组名，形如 `"reaction_002"`、`"reaction_107"` |

---

## 4. 循环前的四个变量（纪律 6：数整个函数的，放循环外）

```python
        total = np.zeros(len(E))
        at_i0 = {}
        i0 = int(np.searchsorted(E, E_TEST, side="right")) - 1
        n_add = 0
```

| 变量 | 是什么 | 为什么在循环外 |
|---|---|---|
| `total` | 和 `E` 一样长的全 0 数组，累加器 | 🔴 放进循环 → 每圈清零 → 只剩最后一个道，**不报错**（9/4、9/5、9/7 三次同一个岔路口） |
| `at_i0` | 空字典：键 = MT 号（**整数**），值 = 这个道在 `i0` 处的截面 | 攒所有道的 |
| `i0` | 网格里「≤ E_TEST 的最后一个点」的下标 | 只和 `E`、`E_TEST` 有关，算一次 |
| `n_add` | 真正加进 total 的道数 | 计数器 |

**`i0` 的算例**（数字是假的，方便算）：`E = [0.011, 0.018, 0.0246, 0.0301, 0.042]`，`E_TEST = 0.0253`

```
searchsorted(E, 0.0253, side="right")  → 3     （0.0253 插在下标 3 前面才能保持递增）
减 1                                    → i0 = 2，E[2] = 0.0246  ≤ 0.0253 ✓
```

真 B10 库里 `E[i0] = 0.024638 eV`（xslib 原注释里的数）。`int(...)` 是把 numpy 的整数转成 Python 整数。

---

## 5. 循环：每个道做什么

```python
        for name in sorted(names):
            rx = root["reactions"][name]
            mt        = rx.attrs["mt"]
            redundant = rx.attrs["redundant"]
            xs_ds = rx[T]["xs"]
            thr   = int(xs_ds.attrs["threshold_idx"])
            xs    = xs_ds[:]
```

`sorted(names)`：按名字排序，每次跑顺序都一样。读出的五样和 `load_nuclide` 一样：MT 号、是不是冗余道、截面数据集、阈值下标、截面数组。

### 5.1 阈值对齐（判据 A 那条 assert 抓的事）

有阈值的道（比如 (n,2n)），截面**从网格第 `thr` 个点才开始存**。算例：

```
E   有 6 个点：  E[0] E[1] E[2] E[3] E[4] E[5]
thr = 2
xs  只有 4 个：            xs[0] xs[1] xs[2] xs[3]
                            ↑ 对着 E[2]
```

所以 `len(xs) + thr == len(E)`（4 + 2 = 6）—— 这就是 assert 在验的。
**同一个对齐关系用了两次**：

### 5.2 记下这个道在 `i0` 处的值

```python
            at_i0[int(mt)] = 0.0 if i0 < thr else xs[i0 - thr]
```

`A if 条件 else B` 是**一行写完的 if/else**（条件真取 A，假取 B），等价于：

```
如果 i0 < thr：  这个道在 i0 还没开始（低于阈值）→ 记 0.0
否则：           E[i0] 对着的是 xs[i0 − thr]（上图：i0 = 3 → xs[1]）
```

🔴 冗余道**也记**（这一行在 `continue` 前面）：`__main__` 的判据 C 要拿 MT=107 当参照。
`int(mt)`：库里读出来的是 numpy 整数，转成 Python 整数再当键，之后 `at_i0[107]` 才找得到。

### 5.3 冗余道跳过

```python
            if redundant:
                continue
```

冗余道 = 别的道的和（比如 MT=107 = 800 + 801）。再加一遍就重复了。`continue` = 这一圈后面的不做了，直接下一圈。

### 5.4 判据 E 的位置

`at_i0 < 1e6` 那条 assert 必须在 `continue` **后面**：MT=301（加热数，9.12e9）是冗余道，放前面会把一个根本不参与求和的道拦下来。**assert 挡在它要挡的操作（求和）前面。**

### 5.5 加进去

```python
            total[thr:] += xs
            n_add += 1
```

`total[thr:]` 从第 `thr` 格到末尾，正好 `len(E) − thr` 格 = `len(xs)`，一格对一格加。上图：`total[2:]` 的 4 格 += `xs` 的 4 个。
写成 `thr-1` 会形状不匹配报错；更阴的是 `thr = 0` 时写成 `total[-1:]` —— 负下标从末尾数，只剩最后一格。

---

## 6. 循环后：打印、判据 D、返回

```python
    print(...)
    assert np.all(total > 0), ...
    return E, total, at_i0, i0, awr
```

| 行 | 做什么 |
|---|---|
| `print` | 几个道、加了几个、跳了几个 |
| `np.all(total > 0)` | `total > 0` 得到一个 True/False 数组，`np.all` = 是不是**每一个**都 True。抓：下标错位把 0 留在了不该是 0 的地方 |
| `return` | 🔴 **五个**，顺序 `E, total, at_i0, i0, awr`。调用方（`plot_xs` 等）按这个顺序接，顺序错不会报错 |

注意 `print` 和最后两行**在 `with` 外面**（少一层缩进）：读完数据文件就可以关了，后面不再碰文件。

---

## 7. 对拍块（Claude 写，粘到 `copy_total_xs.py` 最后）

```python
if __name__ == "__main__":
    from xslib import total_xs as total_xs_orig
    for nuc in ["B10", "H1"]:
        E1, t1, a1, i1, w1 = total_xs(nuc, T)
        E2, t2, a2, i2, w2 = total_xs_orig(nuc, T)
        # [Claude assert] 抓：抄写稿和原文在网格、总截面、i0、awr 上有任何一位不同
        assert np.array_equal(E1, E2) and np.array_equal(t1, t2), "%s：E 或 total 和原文不逐位相同" % nuc
        assert i1 == i2 and w1 == w2, "%s：i0 %r vs %r，awr %r vs %r" % (nuc, i1, i2, w1, w2)
        # [Claude assert] 抓：at_i0 少记了道（比如冗余道没记）或记错了值
        assert a1 == a2, "%s：at_i0 不同，抄写稿 %d 个键、原文 %d 个键" % (nuc, len(a1), len(a2))
        print("%s 逐位相同 ✓   total[i0] = %.6f b" % (nuc, t1[i1]))
```

- `from xslib import total_xs as total_xs_orig`：把原文的函数**换个名字**拿进来（和 `import numpy as np` 一个道理），不然和你抄的 `total_xs` 重名，后一个会盖掉前一个。
- `np.array_equal(a, b)`：两个数组形状一样、每一位都一样 → True。

**应该看到**：每个核素先打两行一样的 `[B10] … 个道，加了 … 个，跳过 … 个冗余道`（一行是你的、一行是原文的），然后 `B10 逐位相同 ✓`；H1 同样。最后共 6 行。
