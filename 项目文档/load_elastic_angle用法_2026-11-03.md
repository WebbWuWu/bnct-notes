# `load_elastic_angle` 用法清单 · 2026-11-03（Claude 写）

> 规则 13：先列要用的写法（用过的也讲一遍），例子和项目无关；你写的时候我只给中文描述、一步一步给。
> 今天写：把 H1、O16 弹性散射（MT=2）的**质心系角分布**从库里读出来、按表切好，装进一个字典 —— 只读，不抽样。
> 依据：你 11/1 写的 `my_code\explore\lesson12_elastic_angle.py` 的 `show_angle`（路径、`offsets`、切片都在里面，今天是把「打印」改成「装进字典、返回」）。
> 结构和 `load_thermal` 很像：都是「读一长条 → 按 offsets 切成一张张小表 → 每张一个小字典 → 放进列表」。
> 下一次（抽样）：在一张表里按 pdf 抽 μ_cm，用的是和 11/2 抽 E′ **同一个**二次反解；再从质心系换到实验室系。

---

## 一、名字（名字我起）

| 名字 | 是什么 |
|---|---|
| `load_elastic_angle(lib_dir, nucs)` | 函数：给库目录、核素名的元组（如 `("H1", "O16")`），返回 `angle` |
| `angle` | 返回的大字典，键 = 核素名 `"H1"`、`"O16"` |
| `angle["O16"]["E"]` | 这个核素角分布的入射能量格点（eV），O16 1636 个、H1 153 个 |
| `angle["O16"]["cm"]` | 角分布是不是质心系的（`center_of_mass` 属性，转成 `True` / `False`） |
| `angle["O16"]["tables"]` | 列表，一张入射能量一份；每份是小字典，键 `"mu"`、`"pdf"`、`"cdf"`（都是一维数组，同样长） |
| `ang_E`、`mu_all`、`mu_offs`、`n_pts` | 函数里临时用：和 `show_angle` 里同名、同含义 |
| `b`、`e` | 第 j 张表在 `mu_all` 里的起点、终点（和 `show_angle` 第 54–55 行一样） |
| `mu_v`、`mu_p`、`mu_c` | 切出来的一张表的 μ、pdf、cdf 三行 |

---

## 二、用到的写法（逐个，例子和项目无关）

### 1. 三层嵌套：字典 → 字典 → 列表 → 字典
```python
library = {"北馆": {"floors": 3, "rooms": [{"seats": 40}, {"seats": 25}]},
           "南馆": {"floors": 5, "rooms": [{"seats": 60}]}}
library["北馆"]["rooms"][1]["seats"]     # 25：馆 → 键 → 第几间 → 键
```
取的时候层数要数清：`angle[核素]["tables"][第几张]["mu"]`，四层。
你犯过：两层字典少一层下标（`stodic[k]` vs `stodic[nuc][k]`）；列表套列表少一层。

### 2. 在循环里往外层字典里放东西：键用**循环变量**，不加引号
```python
stock = {}
for fruit in ("apple", "pear"):
    stock[fruit] = {"kg": 0.0}     # 键是 "apple"、"pear"
stock["fruit"] = …                 # ✗ 这是一个叫 "fruit" 的新键
```
你犯过：变量名加引号成了字符串（`"T_TAG"`，10/31）；字典的键用了整个字典（`kerco[nuclides[j]]`）。
外层字典 `angle` 在**循环外面**建空的（纪律 6：数整个函数的放函数开头），每个核素的小字典在**循环里面**建。

### 3. `os.path.join` 拼路径（复习）
```python
os.path.join(r"D:\photos", "trip" + ".jpg")    # D:\photos\trip.jpg
r"D:\photos" + "trip.jpg"                       # D:\photostrip.jpg ✗ 少了斜杠
```
文件名 = 核素名 + `".h5"`，和 `show_angle` 第 28 行一样。

### 4. `with h5py.File(路径, "r") as f:` + 一层层取组（复习）
```python
with h5py.File("weather.h5", "r") as f:
    grp = f["beijing"]["2025"]["temperature"]   # 一层一层取
    grp = f["beijing/2025/temperature"]         # 也可以一次写斜杠路径，结果一样
```
你犯过：`open` vs `h5py.File`（两次）；HDF5 名字拼错（`reactions_301`）。路径照 `show_angle` 第 30、32 行：`核素 → reactions → reaction_002`，再 `product_0/distribution_0/angle`。
数据都要在 `with` 块**里面**读出来（`[:]`）；出了 `with` 文件就关了。

### 5. 属性 `.attrs[...]`：挂在**数据集 / 组对象**上，不在 `[:]` 之后
```python
ds = f["sensor/readings"]
ds.attrs["unit"]          # ✅ 对象上有属性
ds[:].attrs["unit"]       # ✗ [:] 之后是 numpy 数组，没有 attrs
```
今天两个属性：`center_of_mass` 挂在 `reaction_002` 这个**组**上；`offsets` 挂在 `mu` 这个**数据集**上。
你犯过：`.attrs` 用在 `[:]` 之后（两次）；组上的属性当子组取（`root["energy_max"]`）。
`center_of_mass` 读出来是 numpy 的布尔 / 整数，用 `bool(…)` 转成 Python 的 `True` / `False` 再存。

### 6. 每张表多长：`np.diff(np.append(起点们, 总长))`（复习，`load_thermal` 第 36 行同一招）
```python
starts = np.array([0, 4, 9])      # 三段的起点
total = 15                        # 总长
np.diff(np.append(starts, total))   # [4 5 6]：每段多长
```

### 7. 二维数组按行切、一次拆成三个（复习）
```python
grid = np.array([[1.5, 2.5, 3.5, 4.5],
                 [0.2, 0.3, 0.4, 0.5],
                 [7.0, 8.0, 9.0, 6.0]])
r0, r1, r2 = grid[0:3, 1:3]      # 三行各取第 1、2 列 → r0 = [2.5 3.5] …
```
你犯过：切片终点多 +1（`e` 已经是下一张的起点，11/1）；`for` 接的变量个数 ≠ 元组长度。

### 8. 列表攒小字典：`append`（复习）
```python
rooms = []
rooms.append({"seats": 40})      # 放进去一个元素
rooms = {"seats": 25}            # ✗ 把整个列表换掉了
```
你犯过：`=` 换掉攒列表 vs `append`；`append(列表)` vs `+ 列表`。

---

## 三、今天的步骤（只列标题；中文描述我一步一步给）

| 步 | 做什么 | 拿来对的数 |
|---|---|---|
| 1 | 函数头、外层空字典、核素循环、打开文件、取到 `angle` 组和 `center_of_mass` | H1、O16 都是 `True`（质心系） |
| 2 | 读 `ang_E`、`mu_all`、`mu_offs`，算 `n_pts` | H1 153 张、O16 1636 张（11/1 实测） |
| 3 | 按表切、攒进 `tables`，装进这个核素的小字典 | 每张 `mu[0] = −1`、`mu[-1] = +1` |
| 4 | 跑判据 A（我写：和直接读库逐位比 + 11/1 的 A1–A4 搬过来） | O16 0.5 MeV μ̄_cm = 0.417（11/1 实测） |
