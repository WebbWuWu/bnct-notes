# 文献阅读 · COMPASS 第 3 天：Energy interval search（10/25，Claude 出题）

> Zhong, Chen, Teng, Liu, *Introduction to the Monte Carlo dose engine COMPASS for BNCT*, Sci. Rep. 13:11965 (2023)。PDF 在你的「下载」文件夹：`s41598-023-38648-y.pdf`。
> 今天读：**Methods → "Energy interval search algorithm"** 一段（第 3 页下半，从 "Cross-section calculation is one of the most time-consuming steps…" 开始，到第 4 页 "…occupy a significant amount of memory." 为止，约 370 词）+ **Fig. 2** 两张流程图。顺手看一眼 **Table 2** 第一行（第 5 页）。约 25′，手机可做。
> 交：① **中文**一句话总结 ② 下面两题（中文答）。

---

**题 1（式 2 是在干什么）**

式 (2)：u_grid = (ln E − ln E_min) × M / (ln E_max − ln E_min)

设 E_min = 1×10⁻⁵ eV、E_max = 2×10⁷ eV、M = 8000。

(a) 一个 0.0253 eV 的热中子，u_grid 等于多少？取整以后落在第几个新区间？（写出 ln 的数值，一步一步算。）

(b) 如果不取 ln，改成在 E 上**直接均分**成 8000 份，每份多宽（eV）？BNCT 关心的热中子和超热中子（< 10 keV）会落在哪几个新区间里？这样分还有用吗？

(c) 你自己的程序里有一处也是「在 ln E 上均分」：`lesson09_openmc.py` 的 `kur()` 把每个源能群切成 50 个小箱。是哪一行？它和式 (2) 是同一件事的哪两个方向（一个是「给 i 求能量」，一个是「给能量求 i」）？

---

**题 2（和你的 `find_cell` 比）**

(a) 你的 `xs_lookup.py` 里 `find_cell` 找区间用的是论文说的哪一种方法？是哪一行？

(b) 论文说二分查找的时间和节点数是**对数关系**。如果一个核素的能量网格有 12 000 个点，二分最多要比较几次？换成哈希查找，一次查找要做哪两件事？（提示：看 Fig. 2b，以及「M 足够大时，每个新区间里只剩很少几个旧节点」那一句。）

(c) 哈希查找的代价是什么？作者为什么说在 BNCT 里可以接受、在反应堆计算里就不一定？

（附：Table 2 第一行写着换成哈希查找后**整体**只快了 10%。查找本身快了很多倍，整体为什么只快这么一点？想一想就行，判分时我们聊。）
