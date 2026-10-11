# 讲解 · `xs_lookup.py` 逐行（默写块 · 学）

> 2026-10-01 Claude 写，照 `my_code\xs_lookup.py`（2266 字节）逐行讲。
> **怎么用**：开一个新文件 `copy_xs_lookup.py`，放在 `my_code` 根目录，**一行一行照着手敲**。敲完按 Ctrl+F5 跑，跑出 5 行 B-10 的数。
> **对拍**：原文件 `xs_lookup.py` 也跑一次，两边打印的数**逐位相同**（v4 第十一节：「读截面 = 同核素同能量取值逐位相同」）。
> 明天 10/2 默写它，不看任何东西写。这四个函数是 `run_slab` 每一步查截面走的路，也是今天判据 4 里「路 2」的前半截。

文件一共四个函数，调用关系是：

```
load_nuclide  —— 开库，读出 E、各道截面 XS、MT 号、awr        （开始时调一次）
sigma_at      —— 给一个能量 e，返回各道截面和总截面           （每一步调一次）
  ├─ find_cell —— e 落在网格的哪一格（下标 lo）
  └─ xs_at     —— 在那一格里线性插值出一个道的截面
```

---

## 第 1 段 · import 和常量（第 1–9 行）

```python
import os
import h5py
import numpy as np

LIB    = r"E:\BNCT_GPU\lib80x_hdf5"
NUC    = "B10"
T      = "294K"
E_TEST = 0.0253
BARN = 1.0e-24
```

| 行 | 做什么 |
|---|---|
| `import h5py` | 读 HDF5 文件的库。截面库每个核素是一个 `.h5` 文件 |
| `LIB = r"..."` | 🆕 字符串前面的 **`r`** 叫「原样字符串」：里面的 `\` 就是反斜杠本身。不加 `r` 的话，`\` 后面跟某些字母会被当成特殊字符：例如 `"E:\new"` 里的 `\n` 会变成换行，路径就坏了，而且**不报错**。Windows 路径一律加 `r` |
| `NUC`、`T`、`E_TEST` | 只给最下面的 `__main__` 用：核素、温度、测试能量 |
| `BARN = 1.0e-24` | 1 barn = 1e-24 cm²。截面库里存的是 barn，算 Σ = N·σ 时要乘它换成 cm²。`run_slab` 就是从这里 import 的 |

> 常量全大写是约定，意思是「这个数不该被改」。别的文件要用它，**import，不要复制一份**（9/30 你复制过 5 个，那是新的错误类型）。

---

## 第 2 段 · `load_nuclide(nuc, T)`：开库（第 11–38 行）

```python
def load_nuclide(nuc,T):
    path=os.path.join(LIB,nuc+".h5")
    assert os.path.exists(path),"文件不在这里:%s"%path
```

- `nuc+".h5"`：`"H1"` → `"H1.h5"`。
- `os.path.join` 拼出 `E:\BNCT_GPU\lib80x_hdf5\H1.h5`。
- `os.path.exists(path)`：文件存在吗，返回 True / False。核素名拼错（例如写成 `"H-1"`）就会在这一行停下，消息里有完整路径。

```python
    with h5py.File(path,"r")as f:
        root=f[nuc]
```

- 🆕 **`with ... as f:`**：打开文件，名字叫 `f`；缩进块结束的时候**自动关文件**，中途报错也会关。
- `"r"`：只读。
- `root = f[nuc]`：库文件的顶层只有一个键，就是核素名（《库结构说明》§2 的四层树）。

```python
        E=root["energy"][T][:]
        awr=float(root.attrs["atomic_weight_ratio"])
        names=list(root["reactions"].keys())
```

| 行 | 做什么 | H-1 实际值 |
|---|---|---|
| `root["energy"][T]` | 能量网格那个**数据集**（还在文件里，没读出来） | |
| 末尾的 `[:]` | 🔴 **把整个数组真正读进内存**，变成 numpy 数组 | 631 个点 |
| `root.attrs[...]` | `attrs` 是挂在组上的「属性」，不是数组 | 0.999167 |
| `float(...)` | 转成普通的 Python 小数 | |
| `.keys()` | 这个组下面所有子组的名字 | `reaction_002`、`reaction_102` 等 |

🔴 **`[:]` 为什么不能省**：不加 `[:]`，`E` 只是指向文件里那块数据的一个把手。`with` 块一结束文件就关了，这个把手跟着失效，函数 return 出去以后一用就报错。加了 `[:]` 才是一份自己的拷贝。

```python
        mts=[]
        XS=[]

        for name in sorted(names):
            redundant=root["reactions"][name].attrs["redundant"]
            if redundant==1:
                continue
```

- `mts` 和 `XS` 是两个空列表，放在循环**外面**，因为它们数的是「整个核素」（纪律：变量放在它所数的那一层开头）。
- `sorted(names)`：按名字排序。`reaction_002` 排在 `reaction_102` 前面，所以每次跑，道的顺序都一样。
- `redundant==1`：这个道是别的道加起来的和（例如 MT=107 = 800 + 801），跳过不读，否则总截面会算两遍。`continue` 的意思是「这一圈后面的不做了，直接进下一圈」。

```python
            xs_ds=root["reactions"][name][T]["xs"]
            xs=xs_ds[:]
            thr=int(xs_ds.attrs["threshold_idx"])
            assert len(xs)+thr==len(E),"网络或道不完整"
```

- `xs_ds` 是数据集，`xs = xs_ds[:]` 才是读进来的数组（和上面 `E` 的 `[:]` 同一个道理）。
- `threshold_idx`（阈值下标）：**有阈值的反应，库只从阈值那一格开始存**。例：一个道 `thr = 582`，它的 `xs[0]` 对应的是 `E[582]`，不是 `E[0]`。
- `assert len(xs)+thr==len(E)`：从 `thr` 开始存，正好存到最后一格。对不上说明读错了温度或道。

```python
            s = np.zeros(len(E))
            s[thr:] = xs
```

🔴 **对齐**：先造一个和 `E` 一样长的全 0 数组，再把 `xs` 贴到 `s` 的第 `thr` 格到最后。阈值以下截面就是 0（反应发生不了），这是物理，不是缺数据。

**算例**（一个假设的小例子）：`len(E) = 5`，`thr = 2`，`xs = [0.4, 0.7, 0.9]`
```
s = [0, 0, 0, 0, 0]
s[2:] = [0.4, 0.7, 0.9]   →   s = [0, 0, 0.4, 0.7, 0.9]
                                  ↑E[0] ↑E[1] ↑E[2]
```
`s[2:]` 有 5 − 2 = 3 格，`xs` 也是 3 个，正好对上。

```python
            XS.append(s)
            mts.append(int(root["reactions"][name].attrs["mt"]))
    return E,mts,XS,awr
```

- `XS` 是一个列表，**每个元素是一个道的整条截面数组**；`mts` 是同样顺序的 MT 号。`XS[j]` 和 `mts[j]` 说的是同一个道。H-1：`mts = [2, 102]`。
- `return` 在 `with` 块**外面**（缩进少一层）：先关文件再返回。

---

## 第 3 段 · `xs_at(E, s, e, lo)`：一格里的线性插值（第 40–43 行）

```python
def xs_at(E, s, e,lo):
    i=lo+1
    frac = (e-E[lo])/(E[i]-E[lo])
    return s[lo]+frac*(s[i]-s[lo])
```

**公式的来历**：已知两个点 `(E[lo], s[lo])` 和 `(E[i], s[i])`，用直线连起来，求 `e` 处的值。
- `frac` 是 `e` 在这一格里走了几成，0 表示在左端，1 表示在右端。
- 走了几成，截面就从 `s[lo]` 往 `s[i]` 走几成。

**算例（真数，H-1 弹性道，e = 0.0246 eV）**：

```
lo = 241：  E[241] = 0.023975     s[241] = 30.55419
            E[242] = 0.0246375    s[242] = 30.31215
frac = (0.0246 − 0.023975) / (0.0246375 − 0.023975)
     = 0.000625 / 0.0006625 = 0.943396
σ    = 30.55419 + 0.943396 × (30.31215 − 30.55419)
     = 30.55419 + 0.943396 × (−0.24204)
     = 30.55419 − 0.228340 = 30.32585 barn
```
程序算出来是 30.325850，对上了。

> 这个函数**不自己找格子**，`lo` 由调用方给。这样同一个能量查 N 个道，只找一次格子（下面 `sigma_at` 就是这么用的）。

---

## 第 4 段 · `find_cell(E, e)`：e 落在哪一格（第 45–53 行）

```python
def find_cell(E,e):
    if e==E[-1]:
        lo=len(E)-2
    else:
        assert E[0]<=e<=E[-1],"e 必须落在 [E[0], E[-1]] 里，不在就炸"
        i=np.searchsorted(E,e,side="right")
        lo=i-1
    assert E[lo+1]>E[lo],"不递增"
    return lo
```

🆕 **`np.searchsorted(E, e, side="right")`**：在**排好序**的数组 `E` 里找一个位置，把 `e` 插进去以后数组仍然有序。`side="right"` 的意思是：如果 `e` 正好等于某个元素，插在它**右边**。

**算例**：`E = [1.0, 2.0, 3.0]`
| e | `side="right"` 返回 | lo = 返回值 − 1 | 落在哪一格 |
|---|---|---|---|
| 2.5 | 2 | 1 | [2.0, 3.0] ✓ |
| 2.0（正好在网格点上） | 2 | 1 | [2.0, 3.0]，左端点 ✓ |
| 3.0（正好在最后一个点） | **3** | **2** | 🔴 `E[lo+1] = E[3]` 越界 |

这就是开头那个 `if e==E[-1]` 的来历：**e 等于最后一个点时单独处理，放进最后一格** `lo = len(E)-2`。`E[-1]` 是 🆕 负数下标，表示倒数第一个。

- `assert E[0]<=e<=E[-1]`：能量超出表的范围就停。表下限以下的外推不在这里做，在第 7 课的 `sigma_at_ext` 里做（它先判断 `e < E[0]`，就不会走到这条 assert）。
- `assert E[lo+1]>E[lo]`：这一格的宽度大于 0，否则 `xs_at` 里会除以零。《库结构说明》§6 查过，589 个文件里零宽格是 0 个；这条 assert 是兜底的。

---

## 第 5 段 · `sigma_at(E, XS, e)`：所有道一起查（第 55–61 行）

```python
def sigma_at(E,XS,e):
    lo=find_cell(E,e)
    sig=[]
    for j in range(len(XS)):
        sig.append(xs_at(E,XS[j],e,lo))
    total=sum(sig)
    return sig,total
```

- 格子**只找一次**（`lo` 在循环外面），每个道都用这同一个 `lo` —— 所有道共用一张网格，这一点是 `load_nuclide` 里那个对齐保证的。
- `sig` 是各道截面的列表，顺序和 `mts` 一样；`total` 是它们的和。
- **算例**（H-1，e = 0.0246 eV）：`sig = [30.325850, 0.337312]`，`total = 30.663162` barn。

---

## 第 6 段 · `__main__`：拿 B-10 试一下（第 63–77 行）

```python
if __name__ == "__main__":
```
🆕 意思是：**只有直接运行这个文件的时候**才执行下面这一块；别的文件 `from xs_lookup import ...` 的时候不执行。所以 `run_slab` import 它，不会把这 5 行打印出来。

```python
    E, mts, XS, awr = load_nuclide(NUC, T)
    i2   = mts.index(2)
    i800 = mts.index(800)
    i801 = mts.index(801)
    i51  = mts.index(51)
```
`mts.index(2)` 的意思是「MT=2 在 `mts` 列表里排第几」，返回下标。之后用 `XS[i2]` 就能拿到弹性道。**不能直接写 `XS[2]`**：`XS[2]` 是排第 3 的那个道，不是 MT=2。

```python
    i = np.searchsorted(E, E_TEST, side="right")
    print(E[i-1], E_TEST, E[i])
```
打印 0.0253 两边的网格点，看它确实被夹在中间。

```python
    lo = find_cell(E, E_TEST)
    print("elastic  :", xs_at(E, XS[i2],   E_TEST,lo))
    print("n,a0     :", xs_at(E, XS[i800], E_TEST,lo))
    print("n,a1     :", xs_at(E, XS[i801], E_TEST,lo))
    print("n,a total:", xs_at(E, XS[i800], E_TEST,lo) + xs_at(E, XS[i801], E_TEST,lo))
    print("inelastic:", xs_at(E, XS[i51],  E_TEST,lo))
```
- `print("文字", 值)`：逗号隔开的几样东西，打印时中间自动加一个空格。这里没用 `%`。
- `n,a0` + `n,a1` 应该等于库里的 MT=107（9/15 你验过 `MT=107 = 800 + 801` 精确成立）。
- `inelastic`（MT=51，非弹第一能级）在 0.0253 eV 应该是 **0**：它有阈值，热中子打不开。如果这一行不是 0，就是第 2 段的对齐错了。

---

## 抄完自查（不计分）

1. `E` 和 `xs` 后面的 `[:]` 都在吗？
2. `mts=[]`、`XS=[]` 在 `for` 外面吗？`return` 在 `with` 外面吗？
3. `s[thr:] = xs` 的冒号在 `thr` 右边吗？
4. `find_cell` 里 `side="right"` 和 `lo = i - 1` 都在吗？
5. 跑出来的 5 行和原文件逐位相同吗？`inelastic` 是 0 吗？
