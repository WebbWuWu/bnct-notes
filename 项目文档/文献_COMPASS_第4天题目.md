# 文献阅读 · COMPASS 第 4 天：Transport + Dose tally optimization（10/25 晚，Claude 出题）

> Zhong, Chen, Teng, Liu, *Introduction to the Monte Carlo dose engine COMPASS for BNCT*, Sci. Rep. 13:11965 (2023)。PDF 在「下载」：`s41598-023-38648-y.pdf`。
> 今天读：**Methods → "Transportation optimization method" 和 "Dose tally optimization method"** 两段（第 4 页中间到第 5 页上半，到 "…10% to 20% lower than the true statistical error." 为止，约 450 词）+ **Fig. 3**。约 25′，马原课上手机可做。
> 交：① **中文**一句话总结 ② 下面两题（中文答）。

---

**题 1（输运优化：什么时候可以不重算截面）**

(a) COMPASS 在粒子穿进相邻体素时，跳过了 Fig. 3 里的哪一步？跳过要同时满足哪**两个**条件？为什么其中一个条件「在两次碰撞之间一定成立」？

(b) 你的程序里，一段飞行穿过好几层时，`lookup_xs` 一共调用几次？为什么你的一维水模体**天然**就享受到了这个优化？

(c) 到了 M5 三维体素（不同体素可以是不同组织），这个优化在什么情况下会失效？失效时 `fly` 要多做什么？

---

**题 2（计数优化 —— 和你的「先加再平方」是同一件事）**

(a) 式 (3)、(4)：算均值和误差，每个粒子只需要累加哪两样？它们对应你 `end_history` 里的哪两个计数？式 (4) 算的是每个粒子的标准差 σ₁，还是均值的标准误 SE？

(b) 一个粒子两次穿过同一个体素，两次贡献 t₁ = 0.3、t₂ = 0.5。
- 正确的记法：这个粒子往「平方和」里加多少？
- COMPASS 的省事记法：加多少？
- 哪个小？所以误差是**估大了还是估小了**？论文说小了多少？

(c) 你 10/24 写的 `end_history` 里，`kerma_tot_sq` 用的是哪一种记法？如果你也学 COMPASS「省事」，判据 3 丙的「总量 |z| ≤ 3」会出什么问题，是更容易误报，还是更容易漏报？
