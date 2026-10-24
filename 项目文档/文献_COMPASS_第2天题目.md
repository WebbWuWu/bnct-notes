# 文献阅读 · COMPASS 第 2 天：Dose calculation（10/24，Claude 出题）

> Zhong, Chen, Teng, Liu, *Introduction to the Monte Carlo dose engine COMPASS for BNCT*, Sci. Rep. 13:11965 (2023)。
> 今天读：**Methods → "Dose calculation of COMPASS"**（第 2 页下半到第 3 页第一段，到 "...only the neutron dose contributed by ¹⁰B atoms was added to the boron dose." 为止，约 250 词）。约 25′，手机可做。
> 交：① 英文一句话总结（≤ 30 词）② 下面两题（中文答）③ 5 个术语中英（自己从这一段挑）。

---

**题 1（式 1 和你自己的程序）**

式 (1)：D(E) = φ(E) × Σᵢ ρᵢ σᵢ(E) Hᵢ(E)

(a) 这里的 ρᵢ 是什么物理量、单位是什么？它对应你 `lookup_xs` 里的哪个变量？
(b) 论文说 σᵢ 是 "total reaction cross-section"、Hᵢ 是 "average energy deposition of the collision"。你从库里读的 MT=301（`heat`，单位 eV·b）对应式里的哪一部分？如果有人在 `lookup_xs` 里把 `heat` 再乘一次总截面 `tot_j`，结果的单位和大小会错成什么样？

**题 2（"deposited locally" 什么时候对）**

论文说 "The charged particle was deposited locally in COMPASS since the dose in BNCT is mainly contributed by heavy ions rather than electrons"，紧接着又说光子剂量也按式 (1) 累加。

(a) 对 α、⁷Li、反冲质子，"就地沉积"为什么几乎是精确的？
(b) 对光子剂量，这样做相当于讲义第 11 课 §3 里的哪个近似？COMPASS 的体素是 0.75 mm × 0.75 mm × 5 mm（Results 一节），2.2 MeV γ 打出的康普顿电子在水里射程约 0.6–0.7 cm。这个近似在哪里最容易出错？是偏高还是偏低？
