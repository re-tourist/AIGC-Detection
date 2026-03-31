# 实验背景

## 我的提问

把这篇论文的机制，反过来变成你论文的“对照组设计”，设计一个实验去证明：“即便在 strong generator-diverse baseline 上，localized editing 仍然失败”。你和我想到一块了，我也觉得这篇论文是个优秀的baseline，如果我去做实验发现strong generator-diverse baseline 上，localized editing 仍然失败这一结论拿给导师看，他很难不同意我现在local branch + 一致性约束的做法

## ChatGPT的回答

GPT-5.4 Thinking

对，我认为你这个判断是对的，而且很关键。

**Community Forensics 最值得你“反用”的地方，不是直接拿它当 related work 引文，而是把它变成你的反证地基：**

> 在一个已经被证明“通过 generator diversity 就能很强”的 baseline 上，去证明它**仍然**会在 localized editing 上失败。
> 这样你后面的 local branch 就不是“多加一个模块”，而是在补一个 **strong baseline 仍然存在的结构性盲区**。

而这和你 v1.5 里已经写死的主线是完全一致的：你现在的故事本来就不是“再造 detector”，而是“补 failure mode”；具体就是补 localized editing sensitivity 和 deployment perturbation robustness 两个短板。

下面我不给你空泛建议，我直接把它整理成一套**可执行的对照组设计**。

------

# 一、先把要证明的命题写准

你现在真正要证明的，不是：

**命题 A：** local branch 能提升指标。

这个太弱，reviewer 会说只是工程涨点。

你要证明的是：

**命题 B：** 即便在一个 **strong generator-diverse baseline** 上，global image-level detector 依然会系统性地低估 localized editing，尤其当编辑区域小、语义细微、且经过真实后处理时，这种失败会更明显。
因此，需要显式的 local evidence aggregation；再进一步，为了避免局部证据在 JPEG / resize / blur / crop 下进一步崩掉，需要 deployment-aware consistency。

这句话才是你后面整篇论文的脊梁。

------

# 二、为什么这个对照设计有说服力

Community Forensics 已经给了你两个非常硬的前提：

第一，它明确主张：**增加训练 generator 的数量和多样性，会显著提升 unseen generalization**；而且哪怕新增的训练模型几乎全是 latent diffusion，测试到 GAN、pixel diffusion、commercial model 上也会涨。

第二，它还强调：当前领域一个被低估的多样性维度，是 **number of generators**，不是单纯的 image count。它甚至专门控制总图像数，只增加 latent diffusion 模型数量，结果性能依然跨所有 generator type 上升。

所以你如果拿一个普通弱 baseline 去证明“localized editing 很难”，导师和 reviewer 都可能会说：

- 是不是因为 baseline 太弱？
- 是不是因为训练 generator coverage 太差？
- 是不是你还没把 general AIGI detection 做对？

但如果你先把 baseline 尽可能往 Community Forensics 这个方向靠，再证明它对 localized editing 依然差，那这个结论就硬很多。

------

# 三、核心实验思路：把“global 强”与“local 弱”拆开测

你的实验不能只看一个总 Accuracy/AUC。
因为 Community Forensics 这类 strong baseline 很可能在 **global fully-synthetic detection** 上很强，但这不等于它对 **partial/local edit** 也强。你 v1.5 里已经明确要求：要单独报告 localized editing sensitivity，并做 small / medium / large、subtle / obvious 这些 slice。

所以你需要把任务拆成两层：

## 层 1：先确认 baseline 真的强

这是“立地基”。

你至少要让 strong generator-diverse baseline 在下面这些维度上站住：

- clean in-domain / cross-generator image-level detection
- unseen generator
- 至少简化版 degraded robustness

这样你后面说它“localized editing 仍然失败”，才不会被理解成 baseline 没训练好。你的冲刺计划里也把这些列成了最小合格实验。

## 层 2：再专门打 localized editing

这里要把评测集换成 **局部编辑型假图**，而不是整图生成假图。

真正的关键不是“编辑图 vs 真图”这个二分类本身，而是你要把编辑难度分层，让“global pooling 稀释局部证据”这个机制显出来。你自己的主假设 H1 其实已经把这点写出来了：强 VFM 全局表征足以支撑强 image-level AIGI detection，但 global pooling / global decision 会稀释局部伪造信号。

------

# 四、我建议的实验主表结构

你可以把整套实验组织成三个主表 + 两张关键图。

## 主表 1：强 baseline 资格表

目的不是炫耀，而是证明 baseline 合格。

列：

- B0: Frozen backbone + linear probe
- B1: Frozen backbone + MLP probe
- B1-diverse: B1 + generator-diverse training set
- 可选：B1-diverse-strongaug

行：

- fully synthetic clean
- unseen generator
- generator family split
- clean / degraded

你 v1.5 里已经定了 B0/B1/M1/M2 这套命名，这很好，直接沿用。

**你真正需要的不是 B1，而是 B1-diverse。**
也就是：在相同 backbone 和 head 下，只改变训练 fake data 的 generator diversity。

这样你就能复现 Community Forensics 的核心精神：
“不是 architecture 变强，而是 training generator coverage 变强。”

------

## 主表 2：localized editing 失败表

这是最重要的一张表。

列建议：

- B1
- B1-diverse
- M1 = B1-diverse + local module
- M2 = M1 + deployment-aware consistency

行建议：

- overall localized edit detection
- small edit
- medium edit
- large edit
- subtle edit
- obvious edit
- object edit
- stuff/background edit

这张表要回答的问题非常明确：

1. **B1 → B1-diverse** 是否能提升 localized editing？
   大概率会有一点提升，但我预期不会解决核心问题。
2. **B1-diverse → M1** 是否主要在 small/subtle/background 这类 slice 上提升？
   这是 local branch 存在的主要证据。
3. **M1 → M2** 是否主要在 degraded localized slice 上提升？
   这是 consistency 合理性的证据。

这和你计划里写的 “module-to-failure-mode alignment” 完全对应：
local module 对 localized failure，consistency 对 perturbation failure。

------

## 主表 3：clean / degraded localized robustness 表

这一张表是为了防止别人说你 consistency 只是普通增强 trick。

列：

- B1-diverse
- M1
- M2
- M2 w/o realistic consistency
- M2 w/ generic aug consistency

行：

- localized-clean
- localized-JPEG
- localized-resize
- localized-blur
- localized-crop
- robustness drop

如果你发现：

- M1 在 clean localized 上涨最多
- M2 在 degraded localized 上进一步稳住
- 而 generic augmentation consistency 不如 realistic perturbation consistency

那你的 v1.5 叙事就非常顺了。因为你原文就写的是 **deployment-aware consistency**，不是普通一致性口号。

------

# 五、最关键的一张图：把“global 强、local 弱”可视化出来

你需要一张图，直接打导师和 reviewer 的直觉。

## 图 1：edit area ratio vs detection score

横轴：编辑面积占比
纵轴：fake score / recall / AUROC

曲线：

- B1
- B1-diverse
- M1
- M2

你想看到的现象是：

- B1-diverse 在大编辑区域上已经不错
- 但当 edit area ratio 变小时，分数明显塌
- M1 曲线在小区域段显著抬升
- M2 在加 JPEG / resize 后曲线掉得更慢

这张图最能说明问题，因为它把“global pooling 稀释 local evidence”翻译成了一个连续现象，而不是一句口号。你的冲刺计划里也已经把 localized slice 图列为核心产出之一。

------

# 六、数据集该怎么搭，才能真正证明这件事

这里要非常小心。你要证明的是 **strong generator-diverse baseline 在 localized editing 上仍失败**，那训练集和测试集的构造就不能乱。

## 训练集

建议分两路：

### 路 1：global synthetic pretraining / main training

fake 主要来自 generator-diverse fully synthetic images。
这是你向 Community Forensics 借力的部分。

### 路 2：localized edit finetuning 或混合训练

加入局部编辑型数据，但不要让它淹没总体训练分布。
否则 reviewer 会说你只是在“给模型喂更多 localized 样本”。

更好的做法是：

- 先用 generator-diverse global fake data 立住 baseline
- 再用受控比例的 localized edit data 做后续训练或 joint training
- 保持所有模型训练数据完全一致，只改模块

这样你就能公平比较 B1-diverse、M1、M2。

------

## 测试集

测试集必须至少分四组：

1. **fully synthetic unseen generators**
   证明 baseline 强
2. **localized edits clean**
   证明 baseline 在你关心任务上不够强
3. **localized edits degraded**
   证明 deployment perturbation 会进一步伤害 local evidence
4. **localized edits by edit size / subtlety / semantic region**
   证明失败是结构性的，而不是随机样本波动

------

# 七、你需要的关键对照，不然 reviewer 会攻击你

这里我替 reviewer 先攻击你一遍。

## 攻击 1：是不是训练数据不公平

所以你必须固定：

- backbone
- input resolution
- train steps
- augmentation budget
- localized train data ratio

只允许变化：

- 是否有 generator-diverse fake pretraining / training
- 是否有 local module
- 是否有 deployment-aware consistency

这个是你阅读指南里明确要求的 fairness control。

## 攻击 2：是不是 local 模块只是多参数带来的提升

所以最好再加一个参数量接近的对照：

- B1-diverse + bigger MLP
- B1-diverse + naive multi-crop / concat

如果这些都不如你的 local evidence aggregation，那么“不是堆参数”这个点就会更稳。

## 攻击 3：是不是只要加更多 localized training data 就行

这个攻击很强，你必须提前防。

建议加一个控制实验：

- B1-diverse + more localized samples
- M1 + same localized samples

如果 M1 仍然在 small/subtle slice 上更强，那就说明问题不只是数据量，而是 global decision mechanism 本身有盲区。

## 攻击 4：是不是只靠 threshold calibration

Community Forensics 里有一句很值得你记：多 generator diversity 可能改善了 accuracy threshold calibration。

所以 localized setting 下你不能只报 accuracy，最好同时报：

- AUROC
- AUPR / F1
- fixed-threshold recall on fake
- calibration-like 指标或至少 threshold sensitivity

否则别人会说你只是阈值没调好。

------

# 八、真正能打导师的“最小实验闭环”

如果你想先做一个最小可证伪版本，我建议不是一下子全铺开，而是按这个顺序：

## Step 1：做一个 strong generator-diverse baseline

用 frozen VFM + MLP probe，训练 fake 数据从窄 generator 集扩到宽 generator 集。
先在 fully synthetic unseen-generator 上确认它真的更强。

这一步是在复现 Community Forensics 的精神，而不是复现它全量数据集。关键是方向一致：**控制 backbone/head，不断扩大 generator diversity。**

## Step 2：把这个 baseline 拿去测 localized edits

你很可能会看到：

- overall 还行
- 但 small/subtle/background edit 掉得很厉害

这一步就是你要拿给导师看的第一张关键图。

## Step 3：只加 local module，跑 localized slice

如果 M1 主要提升在 small/subtle/background，而不是 everywhere 平推，那就说明 local branch 是对症的。

## Step 4：再加 consistency，只测 degraded localized

如果 M2 主要减少 degraded drop，而 clean 基本不坏，那么 deployment-aware consistency 这个故事就立住了。

这和你当前两周闭环计划是高度一致的：先 B0/B1，再 M1，再 M2，最后做主图和 failure case。

------

# 九、你可以直接写给导师看的实验假设

我建议你现在就把假设写得很学术、很硬。

**H1.** Increasing generator diversity substantially strengthens image-level global AIGI detection and unseen-generator generalization, but does not by itself resolve localized editing sensitivity.
这个前半句由 Community Forensics 支撑，后半句是你要亲自验证的。

**H2.** The residual failure of strong generator-diverse baselines is concentrated on small-area, subtle, and background/stuff localized edits, consistent with the hypothesis that global pooling dilutes sparse local forgery evidence.
这句直接对应你 v1.5 的 H1/H2。

**H3.** A local evidence aggregation module mainly improves localized slices, while deployment-aware consistency mainly improves degraded localized slices, demonstrating module-to-failure-mode alignment.
这句对应你整个方法设计的核心正当性。

------

# 十、我替你做一个更尖锐的判断

我同意你的直觉：**如果你真的做出来“strong generator-diverse baseline 仍然在 localized editing 上失败”这个结果，导师很难再反对你走 local branch + consistency 这条线。**

但我也要泼一点冷水：

真正有杀伤力的，不是“它失败了”这句话本身，而是你要证明：

1. 它不是因为 baseline 弱而失败
2. 它不是因为训练数据窄而失败
3. 它不是因为阈值没调好而失败
4. 它失败得是**有结构的**：集中在 small/subtle/background/degraded 这些 slice
5. 你的模块提升也不是 everywhere 小涨，而是精准补这几个 failure mode

一旦这 5 点站住，你的论文就不再是“我也加了个 local branch”，而会变成：

> 在 strong generator-diverse baseline 已经建立 global generalization 优势的前提下，我们证明其 localized failure 仍是结构性存在，并提出最小必要改动去补这一盲区与其在部署扰动下的进一步退化。

这个叙事是很硬的。

------

# 十一、我建议你现在立刻固化成文档的一页内容

你现在最该做的不是继续抽象讨论，而是把这套内容固化成一个小文档，名字就叫：

**`localized_failure_on_strong_baseline_protocol.md`**

里面只写四部分：

- 研究命题
- baseline 组别
- localized slice 设计
- 预期支持/反驳结果

这样你后面不容易漂。

如果你愿意，我下一条就直接帮你把这份文档写出来，按你项目里一贯的“可交给 codex / 可直接落实验”的风格来写。