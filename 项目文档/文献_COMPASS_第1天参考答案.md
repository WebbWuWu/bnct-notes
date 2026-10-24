# 文献阅读 · COMPASS 第 1 天参考答案：Abstract + Introduction（10/24，Claude 写）

> Zhong, Chen, Teng, Liu, *Introduction to the Monte Carlo dose engine COMPASS for BNCT*, Sci. Rep. 13:11965 (2023)。
> 你 10/23 晚上自己做过第 1 天。昨天的两道题没存进文件，所以下面用的是 10/24 补出的两道题；参考答案供你对照，不判分。

---

## ① 一句话总结（≤ 30 词）

> COMPASS is a BNCT-dedicated continuous-energy Monte Carlo dose engine, parallelized with MPI/OpenMP, that matches MCNP6 dose distributions while running faster than general-purpose codes.（23 词）

要点：**专用**（不是通用程序）· **连续能量**（不是多群）· **并行**（MPI + OpenMP，是 CPU 并行，不是 GPU）· **和 MCNP6 对上**· **更快**。

---

## ② 两道题

**题 1**：作者列了用通用蒙卡程序（MCNP、PHITS）做 BNCT 治疗计划的三个缺点。是哪三个？其中第 (2) 条里 "the computation time is proportional to the square of the statistical accuracy" 和第 4 课的 SE ∝ 1/√N 是什么关系？照字面对不对？

- 三个缺点：
  1. 不是为 BNCT 开发的，缺少医疗软件要求的质量控制和测试，难以满足监管对可靠性、安全性的要求；
  2. 功能太全：截面库和子程序太多，难以针对一个用途优化 → 算得慢，病人一多、或者治疗当天要临时改计划时，统计精度跟不上；
  3. 功能不是按 BNCT 场景定制的，很难准确描述 BNCT 的计算模型，**尤其是束流源的定义**。
- 和 SE 的关系：SE = σ₁ / √N，计算时间 ∝ N，所以 **时间 ∝ (σ₁ / SE)²**，也就是和「相对误差的平方」成**反比**。误差减半，时间要 4 倍。
- 照字面：如果 "accuracy" 理解成「精度 = 1 / 误差」，这句话对；如果理解成「统计误差」本身，就说反了。论文的措辞不严谨，面试时用你自己的说法：**时间 ∝ 1 / R²**。
- 用你今天的数算一遍：10 万条 519 s，H1 总 kerma 的 R = 2.3%。要压到 1%，历史数要乘 (2.3 / 1)² ≈ 5.3 倍，约 46 分钟 —— 这就是要上 GPU 的理由。

**题 2**：作者为什么认为 Lee 等人的 GPU 方法「提速也没有意义」？多群和连续能量差在哪？你的程序属于哪一种？

- Lee 等人用 GPU + **多群**蒙卡算中子通量；在头部 CT 体素模型上，通量和吸收剂量的平均绝对百分误差分别是 3.98%、3.91%，对放疗来说不可接受 —— 精度不够，快也没用。
- 区别：
  - **多群**：把能量切成若干个群，每群里的截面事先按一个**假定的能谱**加权平均成一个数；输运时中子能量只记「在第几群」。真实能谱和假定的不一样时，群截面就有偏差；共振、热区上散射这些细节被抹平。
  - **连续能量**：截面直接用评价库的逐点表，在中子**此刻的能量**上插值（你的 `find_cell` + `xs_at`）；散射运动学也按连续能量算（你的 `scatter`、自由气体 fgk）。
- 你的程序是**连续能量**：ENDF/B-VIII.0 逐点 HDF5 库 + 插值 + 自由气体。⚠️ 别混：你的**源能谱**是 KUR 三群表（只决定中子从哪个能量出发，群内按 1/E 抽连续的能量），**输运**是连续能量。
- 🔴 **和你项目的关系（面试可以讲）**：COMPASS 指出「GPU + 多群 → 快但不准」「CPU + 连续能量 → 准但慢」。你的项目是 **GPU + 连续能量**，正好对准这个空档。

---

## ③ 5 个术语（参考，你挑的不一样也没关系）

| 英文 | 中文 |
|---|---|
| treatment planning system (TPS) | 治疗计划系统 |
| general-purpose Monte Carlo code | 通用蒙特卡罗程序 |
| continuous-energy Monte Carlo | 连续能量蒙卡 |
| multi-group method | 多群方法 |
| voxel model | 体素模型 |

（文中还有：compound biological effectiveness (CBE) 化合物生物效应、relative biological effectiveness (RBE) 相对生物效应、statistical accuracy 统计精度。）
