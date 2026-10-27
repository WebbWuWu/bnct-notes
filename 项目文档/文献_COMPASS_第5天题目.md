# 文献阅读 · COMPASS 第 5 天：Results（10/26 晚，Claude 出题）

> Zhong, Chen, Teng, Liu, *Introduction to the Monte Carlo dose engine COMPASS for BNCT*, Sci. Rep. 13:11965 (2023)。PDF 在「下载」：`s41598-023-38648-y.pdf`。
> 今天读：**Results** 三段 —— "Algorithm acceleration effect…"（第 6 页，含 **Table 2**、式 5）· "Accuracy verification of dose between COMPASS and MCNP6"（第 6–8 页，看 **Table 3、5** 和式 6 下面那段；gamma pass rate 那几段扫一眼即可）· "Computational speed comparison…"（第 9 页，含式 8、**Table 7**）。约 25′，手机可做。
> 交：① **中文**一句话总结 ② 下面两题（中文答）。
> 附：第 4 天遗留 —— 回头看一眼式 (4)：根号里是 (Σtᵢ²/N − mean²) / (N − 1)。按 10/26 说的判法（方差外面有没有**又除一次** N 或 N−1），它是 σ₁ 还是 SE？一句话答。

---

**题 1（FOM：怎么公平地比「快」）**

式 (8)：FOM = 1 / (R² T)，R 是相对标准误（SE / 均值），T 是计算时间（s）。

(a) Table 7 里 COMPASS 的硼剂量：R = 0.0123，T = 22243 s。算出 FOM，和表里的 0.297 对一下。

(b) 为什么对**同一个程序**，FOM 基本不随粒子数 N 变？提示：R 和 N 是什么关系（第 4 课），T 和 N 呢？

(c) 用你自己的数：10 万条水模体跑了 519 s，H1 总 kerma 的 R = 0.023。你的 FOM 是多少？如果要把 R 压到 1%，大约要跑多久？今晚 2 万条一个种子约 110 s —— 它的 R 应该是多少（不用跑，用 (b) 推）？

---

**题 2（「差 1%」算不算差：统计显著 vs 临床可接受）**

式 (6)：相对偏差 = |D_MCNP − D_COMPASS| / D_MCNP。括号里的百分数是各自的相对统计误差 R。

(a) Table 3，Brain Stem 的**最大**硼剂量：COMPASS 4.36625e−8（1.0%），MCNP6 4.4742e−8（1.15%）。用你判据 3 的办法算 z =（两者之差）/ √(SE₁² + SE₂²)。|z| 是大于还是小于 3？论文说这 2.41% 的偏差「统计误差再小一点就会变小」—— 和你的 z 对得上吗？

(b) Table 5，Tumor 的**平均**光子剂量：COMPASS 2.70869e−8（0.08%），MCNP6 2.67898e−8（0.03%）。同样算 z。

(c) 论文的结论是「两者没有显著差别」，理由是偏差都 < 3%、临床可接受。结合 (b)：从统计上看这句话站得住吗？「统计上显著」和「临床上要紧」是不是一回事？你的判据 3 检验的是哪一个？
