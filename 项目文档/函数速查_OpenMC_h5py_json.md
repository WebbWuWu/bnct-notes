# 函数速查：OpenMC · h5py · json（10/25 起，Claude 整理）

> 用途：有空的时候翻着回顾。**不是默写清单**，不用背参数顺序，认得出、知道它干什么、知道自己在哪儿栽过就行。
> 每一条：**写法 → 做什么 → 你在哪里用过 → 🔴 你踩过的坑**。行号是 10/25 的 `my_code`。
> 以后新学的（比如今天方案乙的 `openmc.data`）我会往这里补。

---

## 一、json：把结果存成文本 / 读回来

你所有的结果文件（`dose_*.json`、`openmc_*.json`、`water_*.json`）都靠这两个函数。

| 写法 | 做什么 | 用过 |
|---|---|---|
| `with open(路径, "w") as f:` | 打开文件准备**写**；`with` 块结束自动关文件 | `lesson08_dose.py` 119 |
| `json.dump(字典, f)` | 把字典写进文件 | `lesson08_dose.py` 120（`save_result`）、`lesson11_openmc.py` 104 |
| `with open(路径, "r") as f:` | 打开文件准备**读** | `lesson08_dose.py` 128 |
| `json.load(f)` | 读出来，还原成字典 | `lesson08_dose.py` 129（`load_result`）、`lesson09_compare.py` 67–76 |

**能存进 json 的东西**：字典、列表、字符串、整数、浮点数、`True/False`、`None`。

- numpy 数组**存不进去**，要先 `.tolist()` 变成列表（`lesson09_openmc.py` 131、133 就是为这个）。
- 字典的键**存完都变成字符串**：存 `{3: 1.5}`，读回来是 `{"3": 1.5}`。你现在的键都是字符串，没碰上，以后用数字当键要记得。
- 浮点数存进去再读出来**逐位相同**（`check_split.py` 逐位回归就靠这个）。

🔴 **你踩过的坑**
- `open(…, "w")` **会先清空文件**，读的时候要用 `"r"`（10/11）。
- **结果装一个字典、存的是另一个**（10/14）。
- **json 里的键当变量用**：`sigma_x` 是 `d["sigma_x"]`，不是变量 `sigma_x`（10/17）。
- **`name` 一会儿是文件名、一会儿是字典**（10/17）：读进来的字典起一个和路径不一样的名字（你在 `lesson09_compare.py` 用 `path1` / `book1`，这个习惯好）。
- 拼路径一律 `os.path.join(文件夹, 文件名)`，**不要字符串相加**（10/14 两次，10/25 `XML_ISO` 一次）。

---

## 二、h5py：直接读截面库的 `.h5` 文件

### 2.1 库文件长什么样（以 O16 为例）

```
O16.h5
└─ O16                         组；.attrs["atomic_weight_ratio"] = awr
   ├─ energy
   │   └─ 294K                 数据集：能量网格（eV），一列数
   ├─ kTs
   │   └─ 294K                 数据集（只有一个数）：kT（eV）
   └─ reactions
       ├─ reaction_002         组；.attrs["mt"]、["redundant"]、["Q_value"]、["label"]
       │   └─ 294K
       │       └─ xs           数据集：截面（b）；.attrs["threshold_idx"]
       ├─ reaction_102 …
       └─ reaction_301         MT=301 加热系数（eV·b），也存在 xs 里
```

**组（group）**像文件夹，里面装别的东西，**取不出数**；**数据集（dataset）**才是数。

### 2.2 写法

| 写法 | 做什么 | 用过 |
|---|---|---|
| `with h5py.File(路径, "r") as f:` | 只读打开 | `xs_lookup.py` 15、`lesson07_freegas.py` 28、`lesson11_mt301.py` 27 |
| `root = f[nuc]` | 进到核素那一层组 | 同上下一行 |
| `root["energy"][T][:]` | 数据集 → **整列取成 numpy 数组** | `xs_lookup.py` 17 |
| `root["kTs"][T][()]` | **只有一个数**的数据集 → 取出那个数 | `lesson07_freegas.py` 30 |
| `root.attrs["atomic_weight_ratio"]` | 读**属性**（贴在组或数据集上的小标签） | `xs_lookup.py` 18 |
| `list(root["reactions"].keys())` | 这个组里有哪些名字（`reaction_002`、`reaction_102`…） | `xs_lookup.py` 19 |
| `"reaction_301" in names` | 有没有这一项（True / False） | `lesson11_mt301.py` 13 |
| `float(…)`、`int(…)` | 属性读出来是 numpy 类型，转成普通数 | `xs_lookup.py` 18、30 |

### 2.3 一个固定套路：阈值下标补零

阈值反应（比如 (n,α) 在某个能量以下不发生）的 `xs` **只存阈值以上那一段**，前面省掉的点数就是 `threshold_idx`。补成和能量网格一样长：

```
s = 全零数组，长度 = 能量网格的点数
s[threshold_idx:] = xs
```

`xs_lookup.py` 30–34、`lesson11_mt301.py` 35–36。判据永远是：**`len(xs) + threshold_idx == len(E)`**（对不上说明温度组读错了，或者道不完整）。

### 2.4 跳过「加和道」

`.attrs["redundant"] == 1` 的道是别的道加起来的（比如 MT=1 总截面、MT=101 吸收），抽反应时要跳过，否则会算两遍。`xs_lookup.py` 26–28。**但 MT=301 也是 redundant**，读 heating 时要专门去取（`lesson11_mt301.py` 30）。

🔴 **你踩过的坑**
- **`.attrs[...]` 只在 h5py 对象上有**；Python 字典用 `["键"]`（10/10）。
- **字典键 `"kT"` vs HDF5 组名 `"kTs"`**。
- **`reaction_301` 写成 `reactions_301`**：`in` 只返回 False，悄悄跳过，不报错（10/22）。
- **把组当数据集用 `[()]`**（10/22）：组里没有数。
- **`XS[道][格点]`：行是道，列是格点**（10/10 两次反）。
- 数据要**在 `with` 块里面**用 `[:]` 取出来；出了 `with` 文件已经关了。

---

## 三、OpenMC：搭模型 → 跑 → 读结果

一个 OpenMC 计算 = 四个 xml 文件（材料、几何、设置、tally）+ 一个截面库清单。你的 `lesson09_openmc.py` 每个函数正好管一块。

### 3.1 截面库

| 写法 | 做什么 | 用过 |
|---|---|---|
| `openmc.config['cross_sections'] = 路径` | 告诉 OpenMC 用哪份 `cross_sections.xml` | `lesson09_openmc.py` 18 |

⚠️ 这一行在**被 import 时**就会执行（它不在函数里）。今天方案乙要换库，换库那一行必须写在 import 后面。

### 3.2 材料 `openmc.Material`

| 写法 | 做什么 | 用过 |
|---|---|---|
| `m = openmc.Material(name='water')` | 新建材料，名字自己起 | `lesson11_openmc.py` 66 |
| `m.add_nuclide('H1', 份额, 'wo')` | 加核素；`'wo'` = 质量份额，`'ao'` = 原子份额 | `lesson11_openmc.py` 67–69 |
| `m.set_density('g/cm3', ρ)` | 密度 | `lesson11_openmc.py` 70 |
| `m.temperature = 294` | 温度（K），决定用库里哪个温度的截面 | `lesson11_openmc.py` 71 |
| `m.add_s_alpha_beta("c_H_in_H2O")` | 加 S(α,β) 热散射（水里 H 的化学键） | `lesson09_openmc.py` 165 |
| `m.get_nuclide_atom_densities()` | 返回 {核素: 数密度}，**单位 atom/(b·cm)** = /cm³ × 1e-24 | `lesson11_openmc.py` 80 |
| `openmc.Materials([m])` | 材料集合（导出 xml 用） | `lesson09_openmc.py` 98 |

🔴 `'wo'` 的份额会被 OpenMC **重新归一化**（10/13 抓到的对齐坑）；OpenMC 换算数密度用的是它**自己的原子质量表**，和你的 awr × M_N 差约 1e-7。

### 3.3 几何

| 写法 | 做什么 | 用过 |
|---|---|---|
| `openmc.XPlane(x0=7.3, boundary_type='reflective')` | x = 7.3 的平面；边界条件：`'reflective'` 反射、`'vacuum'` 真空（出去就没了） | `lesson09_openmc.py` 33–38 |
| `-xp1`、`+xp2` | 平面的**负侧 / 正侧**（x < 7.3 / x > −7.3） | 40 |
| `A & B` | 两个区域的**交集**（同时满足） | 40 |
| `openmc.Cell(fill=mat, region=bou)` | 栅元：这块区域里装这种材料 | 42 |
| `openmc.Geometry([c])` | 整个几何 | 43 |

### 3.4 源

| 写法 | 做什么 | 用过 |
|---|---|---|
| `openmc.stats.Point((0, 0, 1e-6))` | 点源位置 | 100 |
| `openmc.stats.Monodirectional((0, 0, 1))` | 只朝一个方向（+z） | 101 |
| `openmc.stats.Tabular(edges, dens, interpolation="histogram")` | 分段常数的能谱；**`dens` 是概率密度**（份额 ÷ 箱宽），最后补一个 0 和 edges 一样长 | 64 |
| `openmc.stats.Discrete([37.2], [1.0])` | 离散能量：只有 37.2 eV | 196 |
| `openmc.IndependentSource(space=…, angle=…, energy=…)` | 把位置、方向、能量拼成一个源 | 102 |

🔴 `Tabular` 的 p 是**密度**不是份额（10/13 抓到的第二个对齐坑）。

### 3.5 设置 `openmc.Settings`

| 写法 | 做什么 | 用过 |
|---|---|---|
| `st.run_mode = 'fixed source'` | 固定源（不是临界计算） | 105 |
| `st.particles`、`st.batches` | 每批粒子数、批数；总粒子数 = 两者相乘 | 106–107 |
| `st.seed` | 随机数种子 | 108 |
| `st.source = S` | 源 | 109 |
| `photon_transport` | **默认 False**，没写就是不开光子输运 | — |

### 3.6 Tally（要记什么）

| 写法 | 做什么 | 用过 |
|---|---|---|
| `openmc.RegularMesh()` + `.dimension`、`.lower_left`、`.upper_right` | 规则网格；你用 [1, 1, 30] = 只沿 z 切 30 层 | 68–71 |
| `openmc.MeshFilter(grid)` | 「按网格分开记」的过滤器 | 72 |
| `openmc.CollisionFilter([0])` | 只记**还没碰撞过**的中子（判据 1 未碰撞通量） | 77 |
| `t = openmc.Tally(name='…')` | 新建 tally，名字**自己起** | 88 |
| `t.filters = [过滤器]` | 按什么分开记；**不写 = 整个模型一个数**（判据 3 丙的总量） | 89 |
| `t.nuclides = ['H1']` | 只记这个核素的贡献 | 91 |
| `t.scores = ['heating']` | 记什么；**必须是 OpenMC 认的关键词**：`flux`、`heating`、`(n,gamma)`、`(n,a)`、`(n,p)` | 92 |
| `openmc.Tallies()` + `.append(t)` | tally 集合 | 86、93 |

🔴 **tally 的 `name`（你起的标签）vs `scores`（OpenMC 认的关键词）**搞反过（10/14）；**键前缀 vs tally 名拿反**。

### 3.7 导出、运行

| 写法 | 做什么 | 用过 |
|---|---|---|
| `x.export_to_xml(路径)` | 材料 / 几何 / 设置 / tally 各导一个 xml | 115–118 |
| `openmc.run(cwd=文件夹)` | 在这个文件夹里跑 OpenMC | 120 |
| 结果文件名 | `statepoint.<批数>.h5`，在同一个文件夹里 | 121 |

### 3.8 读结果

| 写法 | 做什么 | 用过 |
|---|---|---|
| `with openmc.StatePoint(路径) as sp:` | 打开结果文件 | 126 |
| `sp.get_tally(name='…')` | 按你起的名字取一个 tally | 127 |
| `t.mean`、`t.std_dev` | 均值和**均值的标准误**（批与批之间算的），numpy 数组，形状是多维的 | 128–129 |
| `.flatten().tolist()` | 压成一维 → 变成列表 → 才能存 json | 130–133 |

🔴 `.std_dev` 不是 `.std.dev`（10/14）；`.tolist` 别少括号。
OpenMC 的 heating 单位：**eV / 源粒子**，和你的 `kerma_sum` 一样，不用换算。

---

## 四、对照表：同一件事，三个地方的写法

| 要做的事 | Python 字典 / 列表 | h5py | OpenMC 对象 |
|---|---|---|---|
| 按名字取 | `d["键"]` | `f["组名"]` | `sp.get_tally(name=…)`、`nuc.reactions[2]` |
| 有哪些名字 | `d.keys()` | `f["组"].keys()` | — |
| 取元数据 | — | `.attrs["名字"]` | 直接点属性：`.temperature`、`.name` |
| 取成数组 | — | `ds[:]`；单个数 `ds[()]` | `.mean`、`.std_dev` |
| 存盘 | `json.dump` | （你没写过 h5） | `.export_to_xml`、`export_to_hdf5`（10/25 新） |

---

## 五、openmc.data：读改一个核素的截面数据（10/25 方案乙，`lesson11_iso.py`）

| 写法 | 做什么 | 用过 |
|---|---|---|
| `openmc.data.IncidentNeutron.from_hdf5(路径)` | 把一个核素的整份 `.h5` 读成对象 | `make_iso` |
| `nuc.reactions[2]` | 按 MT 号取反应（字典） | `make_iso` |
| `.products[0].distribution[0]` | 出射的第 0 个粒子（中子）的第 0 段分布 | `make_iso` |
| `.angle` → `.energy`、`.mu` | 角分布：一列入射能量 + 同样长的一列「μ 怎么分布」 | `make_iso` |
| `openmc.stats.Uniform(a, b)` | [a, b] 上均匀；`Uniform(-1, 1)` = 质心系各向同性 | `make_iso` |
| `openmc.data.AngleDistribution(能量列表, 分布列表)` | 搭一个新角分布（两个格点就能表示「所有能量都一样」） | `make_iso` |
| `nuc.export_to_hdf5(路径, mode="w")` | 存成新 `.h5`；**`"w"` 覆盖**，默认 `"a"` 第二次跑会报错 | `make_iso` |
| `openmc.data.DataLibrary()` + `.register_file(路径)` + `.export_to_xml(路径)` | 自己生成一份截面库清单（只含登记过的文件） | `make_lib` |

🔴 你踩过的坑：读写用了同一个路径（写回原库会把 `lib80x_hdf5` 覆盖掉）· `Uniform` 里填了能量（应该是 μ 的范围）· 属性名拼错（`angel`）不报错、悄悄新建 —— 判据 ① 专门抓。
详见 `方案乙用法_2026-10-25.md`。
