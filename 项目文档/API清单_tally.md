# tally 新 API 清单（规则 13 · 第 9 课 · 10/14）

> 2026-10-14 Claude 写。OpenMC **0.15.3**（名字和行为都对着 0.15.3 的源码核过：`openmc/mesh.py`、`filter.py`、`tallies.py`、`statepoint.py`、`executor.py`）。
>
> **怎么用**：每个 API 先看「这行得到什么」，再看例子。
> 🔴 **例子是另一个问题**：一根沿 x 方向、40 cm 长的水棒，数「碰过 1 次、2 次的中子」的吸收。
> 名字（`'rod absorb'`）、数字（8 格、±20）、路径（`/home/abc/rod_run`）**全是占位**，别抄进你的文件（10/13 抄过 `'gold foil'` 和 `/home/abc/run1/`）。
>
> 写的时候我只给中文描述（这一步要得到什么），不给代码行。

---

## 0. 一张图：tally 由哪几块拼起来

```
网格 RegularMesh  ──▶  MeshFilter ─┐
                                   ├──▶  Tally（filters + scores） ──▶ Tallies ──▶ tallies.xml
            CollisionFilter ───────┘
                                                       openmc.run ──▶ statepoint.<批数>.h5
                                                                           │
                                                   StatePoint ─▶ get_tally ─▶ .mean / .std_dev（numpy 数组）
                                                                           │
                                                          .flatten().tolist() ─▶ json
```

和你 10/13 写的材料、几何、设置是同一个套路：**造对象 → 放进集合 → 导出 xml**。只是多了「跑」和「读回来」两步。

---

## 1. `openmc.RegularMesh()` —— 一张「打分用的格子」

```python
grid = openmc.RegularMesh()
grid.dimension   = [8, 1, 1]               # x 方向切 8 格，y、z 不切
grid.lower_left  = [-20.0, -3.1, -3.1]     # 格子的左下角 (x, y, z)，cm
grid.upper_right = [ 20.0,  3.1,  3.1]     # 右上角
```

| 这行 | 得到什么 |
|---|---|
| `RegularMesh()` | 一个空的长方体网格对象 |
| `.dimension` | 三个整数，**顺序是 (x, y, z)**：每个方向切几格 |
| `.lower_left` / `.upper_right` | 网格整体的两个对角 |

**算例**：x 方向 40 cm 切 8 格 → 每格宽 (20 − (−20)) / 8 = **5 cm**；第 1 格是 x ∈ [−20, −15]，第 8 格是 [15, 20]。

- 🔴 网格**不是几何**：它不改变中子怎么走，只决定分数记到哪一格。网格比盒子小，盒子里多出来的部分就不计分。
- 🔴 切在哪个方向，看 `dimension` 里**哪个位置**不是 1。切错方向，每格都差不多大（判据 1 第 1 条会响）。
- 格子的编号：从 `lower_left` 那一端往 `upper_right` 那一端数，第 1 格在最小坐标那头。

---

## 2. `openmc.MeshFilter(网格)` —— 按格子分箱

```python
f_grid = openmc.MeshFilter(grid)
```

得到一个 filter，它的箱数 = 网格总格数（这里 8 × 1 × 1 = **8**）。一个事件（这里是「一段径迹」）落在哪一格，分数就记到哪一箱。

---

## 3. `openmc.CollisionFilter(列表)` —— 按「到这一刻碰过几次」分箱

```python
f_col = openmc.CollisionFilter([1, 2])
```

得到 **2 个箱**：「恰好碰过 1 次」和「恰好碰过 2 次」。**列表里没写的次数（0、3、4……）一律不计分**。

OpenMC 内部每个中子有一个计数器，源出生时是 0，每发生一次碰撞加 1（`src/physics.cpp`）。一段径迹记分时，看的就是这个计数器当时的值。

**算例**：一个中子出生后走 2.3 cm 碰第一次，再走 1.7 cm 碰第二次，再走 0.6 cm 被吸收。
- 前 2.3 cm：计数器 = 0 → 上面这个 filter **不收**
- 中间 1.7 cm：= 1 → 记进第 1 箱
- 最后 0.6 cm：= 2 → 记进第 2 箱

---

## 4. `openmc.Tally(name=...)` + `.filters` + `.scores`

```python
t = openmc.Tally(name='rod absorb')
t.filters = [f_grid, f_col]
t.scores  = ['absorption']
```

| 这行 | 得到什么 |
|---|---|
| `Tally(name=...)` | 一个空 tally。**`name` 是你之后从结果文件里找它的钥匙**，起一个自己记得住的 |
| `.filters = [...]` | 一个列表，可以放好几个 filter。总箱数 = 各 filter 箱数**相乘**：8 × 2 = **16** |
| `.scores = [...]` | 一个字符串列表，打什么量。判据 1 用的是 `'flux'`（讲义 §6：径迹长度 / 源粒子，单位 cm，**不除体积**） |

- 多个 filter 时，16 个箱的排法是：**列表里排在后面的 filter 变得最快**。上例是 (格 1, 碰 1 次)、(格 1, 碰 2 次)、(格 2, 碰 1 次)……
- 10/15 写真实量时还会用到 `.nuclides = [...]`（只数某几个核素），今天用不到。

---

## 5. `openmc.Tallies([...])` + `.export_to_xml(路径)`

```python
ts = openmc.Tallies([t])
ts.export_to_xml('/home/abc/rod_run/tallies.xml')
```

和你 10/13 写的 `openmc.Materials([...])` / `.export_to_xml(...)` **完全同一个套路**。
🔴 `tallies.xml` 要和另外三个 xml 放在**同一个文件夹**，OpenMC 跑的时候只在一个文件夹里找。

---

## 6. `openmc.run(cwd=文件夹)` —— 跑

```python
openmc.run(cwd='/home/abc/rod_run')
```

- 得到：OpenMC 在那个文件夹里读四个 xml、开始跑，屏幕上滚出很多输出；跑完**同一个文件夹里多出** `statepoint.<批数>.h5`（批数 40 就是 `statepoint.40.h5`，批数 100 就是 `statepoint.100.h5`）和 `summary.h5`。
- 截面库路径：你文件开头那句 `openmc.config['cross_sections'] = ...` 会顺手设好环境变量，`run` 起的 OpenMC 认得到，不用再设。
- **量速度**：输出最后有一段 `Timing Statistics`，看 `Calculation Rate (active)` 那一行（粒子 / 秒），和 `Total time elapsed`。把这两个数抄下来就行。
- 🔴 再跑一次会**覆盖**同名的 statepoint。
- 返回值是 `None`，结果只在文件里。

---

## 7. `openmc.StatePoint(路径)` + `.get_tally(name=...)` + `.mean` / `.std_dev`

```python
with openmc.StatePoint('/home/abc/rod_run/statepoint.40.h5') as sp:
    t2 = sp.get_tally(name='rod absorb')
    m = t2.mean
    s = t2.std_dev
```

| 这行 | 得到什么 |
|---|---|
| `with ... as sp:` | 打开结果文件，叫它 `sp`；缩进块结束自动关。和你 `read_flux_csv` 里 `with open(...) as f:` 一个道理 |
| `sp.get_tally(name=...)` | 按名字找回那个 tally（名字要和第 4 节里起的**一字不差**） |
| `.mean` | numpy 数组：每个箱的均值（每源粒子） |
| `.std_dev` | numpy 数组：每个箱的 **SE**（均值的标准误，用批均值的离散算）。🔴 **不是 σ₁** |

- 数组形状 `.shape` = **(箱数, 核素数, score 数)**。上例 = **(16, 1, 1)**：三维，后两维只有 1。
- 一个箱的均值是 0 时，OpenMC 把它的 `std_dev` 也记成 0（`tallies.py` 第 548 行起）。判据 1 只比「有数的层」，所以没关系。

---

## 8. numpy：`.shape`、`.flatten()`、`.tolist()` —— 存 json 前要的两步

```python
import numpy as np
a = np.array([[[0.31]], [[0.27]], [[0.12]]])
print(a.shape)          # (3, 1, 1)
b = a.flatten()         # array([0.31, 0.27, 0.12])   —— 压成一维，还是 numpy 数组
c = b.tolist()          # [0.31, 0.27, 0.12]          —— 变成 Python 列表
```

| 这步 | 为什么要 |
|---|---|
| `.flatten()` | 把 (16, 1, 1) 压成 16 个数一排。不压的话存进去是「列表套列表套列表」，读的时候要写三层下标 |
| `.tolist()` | `json.dump` **不认 numpy 数组**，直接放会报 `TypeError: Object of type ndarray is not JSON serializable`。转成 Python 列表才能存 |

两步可以连着写在一行上（先压平再转列表）。`json.dump` 本身你在 `lesson08_dose.save_result` 里写过。

---

## 9. 判据 1 那边会读什么（给你对一下，不用照抄）

判据 1 成品 `my_code\lesson09_check1.py` 默认读：

- 文件：`my_code\outputs\openmc_j1.json`
- 键：`"flux0_mean"`（30 个数，从浅到深）、`"flux0_se"`（30 个数）

**文件名和键名你定**（框架第 2 问只定了「原样存、`_mean` / `_se`」）。和上面不一样就告诉我，我改那个脚本顶上三行。

---

## 10. （12:35 补）`openmc.stats.Discrete(能量列表, 概率列表)` —— 单能源

判据 1 要 37.2 eV 单能源，10/13 你只用过 `Tabular`。单能用这个：

```python
e_dist = openmc.stats.Discrete([14.1e6], [1.0])     # 例子：D-T 聚变中子，14.1 MeV，概率 1
```

| 这行 | 得到什么 |
|---|---|
| 第一个列表 | 可能取到的能量，单位 **eV**（14.1 MeV 要写 14.1e6） |
| 第二个列表 | 每个能量的概率，和第一个一一对应；只有一个能量就写 `[1.0]` |

得到的东西和 `Tabular(...)` 一样，是一个能量分布，交给 `IndependentSource` 的 `energy=`。
两个参数一般写成列表。只有一个数时直接写 `Discrete(14.1e6, 1.0)` 也行（0.15.3 源码里单个数会被自动包成列表），但写成列表更清楚，和多个能量的写法一样。

---

## 11. （10/15 补）真问题 tally 要用的新用法（规则 13，例子都和项目无关）

**① 列表里放元组，for 一次拆出几个值**
```python
FRUITS = [("apple", ["red", "green"], 3.7), ("kiwi", [], 2.4)]
for name, colors, price in FRUITS:
    print(name, len(colors), price)
# apple 2 3.7
# kiwi 0 2.4
```
圆括号括起来的是一个「元组」；元组之间要有逗号（少了会报 `'tuple' object is not callable`）。`for` 后面写几个名字就拆成几个，个数要对上。

**② tally 选核素：`.nuclides`**
```python
t = openmc.Tally(name="fuel fission")
t.nuclides = ["U235", "U238"]     # 列表，里面是字符串
```
名字要和材料里 `add_nuclide` 的一模一样。**不设 = 整个材料一起算**（通量、(n,γ) 要的就是这个）。

**③ 这次新用的 4 个 score**（字符串原样写）

| score | 是什么 | 单位（网格一格、每源粒子） |
|---|---|---|
| `'(n,a)'` | 放出 α 的反应次数 | 次 |
| `'(n,p)'` | 放出质子的反应次数 | 次 |
| `'(n,gamma)'` | 辐射俘获次数 | 次 |
| `'heating'` | 这个核素留在这一格里的能量（KERMA，讲义 §7） | eV |

**④ 一个 filter 对象给好几个 tally 用**
```python
f = openmc.EnergyFilter([0.5, 7.9, 64.0])
t1.filters = [f]
t2.filters = [f]       # 同一个 f
```

**⑤ 字典套字典**
```python
book = {}
book["Lin"] = {"math": 87, "art": 92}
print(book["Lin"]["art"])        # 92 —— 先取人，再取科目
```
`json.dump` 存、`json.load` 读回来都还是两层。

**⑥ 空的 tally 容器，往里加**
```python
ts = openmc.Tallies()     # 空的容器（有 s）
t1 = openmc.Tally(name="x")   # 一个 tally（没有 s）
ts.append(t1)
```


## 12. （10/16 补）判据 3、5 要用的新用法（规则 13，例子都和项目无关）

**① 带默认值的参数**（`run(…, seed=1)`）
```python
def brew(cups, sugar=2):        # sugar 不传就是 2
    print(cups, "杯，糖", sugar)
brew(3)            # 3 杯，糖 2
brew(3, sugar=5)   # 3 杯，糖 5
```
有默认值的参数放在没默认值的**后面**。好处：旧的调用一个字不用改。

**② 按名字传参之后，后面全得按名字传**（10/16 `run(…, n_bat=10000, mat)` 报错）
```python
def brew(cups, sugar=2, milk=False): ...
brew(3, sugar=5, True)        # ✗ SyntaxError: positional argument follows keyword argument
brew(3, sugar=5, milk=True)   # ✓
brew(3, 5, True)              # ✓ 全按位置，顺序和定义一致
```
`mat=mat`：左边是**函数定义里的参数名**，右边是**你手里的变量**，正好同名而已。

**③ 字符串拼起来当字典的键**（`my_run` 里 前缀 + `"_sum"`）
```python
stock = {"apple_price": 3.7, "apple_count": 12}
fruit = "apple"
print(stock[fruit + "_price"])    # 3.7
```
这是拼**键名**；拼**路径**照旧用 `os.path.join`。

**④ 返回三个值只要两个：`_` 占位**
```python
def stats():
    return 5, 9, 2
lo, _, hi = stats()      # 中间那个不要
```

**⑤ `json.load` vs `json.dump`**
| | 方向 |
|---|---|
| `json.dump(字典, f)` | 字典 → 写进文件（`open(…, "w")`） |
| `json.load(f)` | 文件里的文字 → 变回字典（`open(…, "r")`） |

**⑥ `%` 格式化：宽度对齐表格**（`mcstat.row()` 就是这么写的）
| 写法 | 意思 |
|---|---|
| `%-16s` | 字符串占 16 格，左对齐 |
| `%8s` / `%8d` | 字符串 / 整数占 8 格，右对齐 |
| `%8.2f` | 小数占 8 格，保留 2 位 |
⚠️ `.2` 写在 `s` 上（`%-8.2s`）是「字符串只留前 2 个字符」—— 10/16 表头 `max_z` 变成了 `ma`。

**⑦ OpenMC：种子、热散射表**
```python
st.seed = 2                                  # Settings 的属性；不设 = 1
moder.add_s_alpha_beta("c_Graphite")         # 给材料加热散射表；名字和 cross_sections.xml 里 materials="…" 一字不差
```
本项目用的是 `"c_H_in_H2O"`（水里束缚的氢；⚠️ 是字母 O，10/16 写成数字 0 过）。只作用于材料里的 H1。

**⑧ 两次独立运行合并**（`merge_two`）
均值 = (m₁ + m₂)/2；SE = √(SE₁² + SE₂²) / 2。
来历：Var(X/2) = Var(X)/4；X、Y 独立 → Var(X+Y) = Var X + Var Y。两份 SE 差不多时 SE合 ≈ SE/√2（= 一次跑两倍历史数）。
