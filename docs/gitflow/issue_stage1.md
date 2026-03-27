# Milestone 1 — Strong Baseline Reproduction (Community Forensics)

## Milestone Title

Milestone 1 — Strong Baseline Reproduction (Community Forensics)

## Background

Milestone 1 是本项目真正进入实验阶段的第一个 milestone。  
它的目标不是做 localized evaluation，也不是开始方法创新，而是先在当前工程框架中复现并站稳一个**强 baseline**。

这个 baseline 的意义非常关键：

- 它是后续 generator-diverse baseline 的起点；
- 它是后续 localized failure 验证的参照系；
- 它决定 reviewer 是否会接受“failure 来自任务本身而不是 baseline 太弱”。

因此，这一阶段必须强调的是：

> 可信复现、工程闭环、结果可追踪。  
> 而不是过早扩展实验范围。

Milestone 1 的策略是：

1. 将 Community Forensics 接入当前工程；
2. 用最小但有效的数据完成 real/fake 二分类闭环；
3. 先做 B0 / B1 两种最小 baseline；
4. 输出第一批稳定的 global detection 结果。

## Suggested Branch Strategy

本 milestone 延续模块化分支策略：

- baseline 接入、feature extraction、probe：`feat/model`
- 数据读取与 binary dataset：`feat/data`
- 训练流程接入：`feat/train`
- 指标与测试流程：`feat/eval`
- checkpoint、脚本整合、结果导出：`feat/scripts`
- 文档与结果表：`docs`

当前阶段仍不建议新增 `feat/baseline`，因为 baseline 还没有形成一个需要独立维护的横向模块。

## Milestone Goal

在统一工程框架内完成 Community Forensics baseline 的最小可信复现，并产出 B0 / B1 的 first-pass 结果。

## Milestone Deliverables

- Community Forensics baseline 接入项目
- real/fake 数据可通过统一 dataloader 读取
- B0：frozen encoder + linear probe
- B1：frozen encoder + MLP probe
- 训练、验证、测试流程闭环
- AUC / Acc 等基本结果
- checkpoint、log、summary 与结果表

## Milestone Acceptance Criteria

- baseline 能成功加载并运行
- B0 和 B1 都能完整跑通 train/val/test
- 至少输出 AUC / Acc 两项指标
- 结果可通过日志和配置回溯
- Stage 2 可以直接在当前 baseline 上扩展 generator diversity

---

# Issue List

- Issue 1-1 — Integrate Community Forensics baseline backbone into project structure
- Issue 1-2 — Implement feature extraction pipeline and frozen encoder control
- Issue 1-3 — Prepare minimal real dataset pipeline
- Issue 1-4 — Prepare minimal fake dataset pipeline
- Issue 1-5 — Build unified binary classification dataset and dataloader
- Issue 1-6 — Implement linear probe baseline (B0)
- Issue 1-7 — Implement MLP probe baseline (B1)
- Issue 1-8 — Integrate baseline training loop into current training framework
- Issue 1-9 — Implement baseline evaluation metrics and inference path
- Issue 1-10 — Run first-pass baseline experiments and verify training sanity
- Issue 1-11 — Save checkpoints, prediction summaries, and experiment artifacts
- Issue 1-12 — Write baseline result table and stage summary

---

## Issue 1-1

### Title
Issue 1-1 — Integrate Community Forensics baseline backbone into project structure

### Background

Stage 1 的第一步不是直接开始训练，而是先把 Community Forensics 的核心 baseline 接入当前项目结构。  
这个过程的重点不是“照搬官方代码”，而是把其核心 backbone / detector 能力接成当前工程中的标准模型模块。

如果这一部分处理不好，后续会出现：

- baseline 只能在原 repo 单独跑，无法纳入当前工程
- model interface 与 train/eval 框架脱节
- 后续 probe 和 generator-diverse 扩展难以复用

### Suggested Branch

`feat/model`

### Goal

将 Community Forensics 的核心 baseline 接入当前项目的 `models/` 体系，使其能够通过统一接口被构建和调用。

### Scope

- 理解官方实现中的 backbone / head 组织方式
- 明确当前项目中需要接入的最小 baseline 组成
- 接入预训练权重或 checkpoint 加载入口
- 对齐输入输出接口
- 保证模型能在当前工程下完成 forward

### Deliverables

- Community Forensics baseline 接入代码
- 模型构建入口更新
- 权重加载逻辑
- 最小 forward 可运行验证

### Acceptance Criteria

- baseline 可通过项目内统一接口加载
- forward 可在 dummy 输入上跑通
- 权重加载逻辑清晰，不依赖手工临时脚本
- 不需要跳回原始 repo 才能运行模型

---

## Issue 1-2

### Title
Issue 1-2 — Implement feature extraction pipeline and frozen encoder control

### Background

Stage 1 的 baseline 不是直接端到端重新设计，而是先建立强 backbone 上的最小 probe 方案。  
因此需要明确：

- encoder 如何提特征
- 特征送入什么 head
- frozen encoder 如何控制

这一步是 B0 / B1 能否成立的前提。

### Suggested Branch

`feat/model`

### Goal

实现 baseline 的特征提取流程，并支持 frozen encoder 设置。

### Scope

- 抽取 backbone feature
- 明确 feature tensor 形状与接口
- 支持 frozen / trainable 状态控制
- 提供给 probe 使用的标准特征入口
- 保证与训练框架兼容

### Deliverables

- feature extraction 代码
- encoder freeze 控制逻辑
- 面向 probe 的统一特征接口

### Acceptance Criteria

- 能稳定输出 probe 所需特征
- frozen encoder 开关可通过 config 控制
- 不存在 feature shape 混乱问题
- B0 / B1 可直接复用此接口

---

## Issue 1-3

### Title
Issue 1-3 — Prepare minimal real dataset pipeline

### Background

Stage 1 不追求最终大规模数据设定，但必须先建立一个稳定的 real data pipeline。  
其任务不是覆盖所有 real source，而是提供一个可控、可复现、可扩展的真实图像来源。

### Suggested Branch

`feat/data`

### Goal

构建最小 real dataset pipeline，为 baseline 二分类训练提供真实样本。

### Scope

- 选择并组织一个最小 real dataset 子集
- 明确 train / val / test 划分
- 实现对应 dataset 类
- 处理路径、标签和 transform 接口
- 保证可扩展到更多 real source

### Deliverables

- real dataset loader
- real split 组织方式
- 数据路径配置示例

### Acceptance Criteria

- real 数据可稳定读取
- train / val / test 边界明确
- 返回字段符合统一 sample schema
- 后续可在不改 trainer 的情况下替换/扩展 real source

---

## Issue 1-4

### Title
Issue 1-4 — Prepare minimal fake dataset pipeline

### Background

在 Stage 1 中，fake data 的目标不是建立 generator diversity，而是先提供一个稳定、单一来源的 fake data pipeline，支撑 baseline 闭环。

关键要求不是规模大，而是：

- 格式统一
- 标签清楚
- 可复现
- 能与 real data 组成干净的二分类任务

### Suggested Branch

`feat/data`

### Goal

构建最小 fake dataset pipeline，为 baseline 的第一轮二分类训练提供伪造样本。

### Scope

- 组织单一 fake source 数据
- 明确 train / val / test 划分
- 实现 fake dataset loader
- 对齐 sample schema
- 对接图像 transforms

### Deliverables

- fake dataset loader
- fake split 配置或组织方式
- 数据读取验证代码

### Acceptance Criteria

- fake 数据可稳定读取
- 标签约定统一
- 能与 real dataset 共同进入同一训练流程
- 为 Stage 2 扩展多生成器留下自然接口

---

## Issue 1-5

### Title
Issue 1-5 — Build unified binary classification dataset and dataloader

### Background

Stage 1 的训练目标是 real/fake 二分类，因此需要一个统一的数据组合层，而不是在训练脚本中分别拼接 real 与 fake。  
如果这一层不独立建立，后续 generator-diverse、localized evaluation 前的预处理将会非常混乱。

### Suggested Branch

`feat/data`

### Goal

构建统一的 binary classification dataset / dataloader 入口，作为 baseline 训练的正式数据接口。

### Scope

- 统一 real / fake 样本组织
- 统一 label 约定
- 构建 train / val / test dataloader
- 接入 transforms 与 batch 组织逻辑
- 适配训练脚本与评估脚本

### Deliverables

- unified binary dataset
- dataloader builder 更新
- 数据读取 sanity check

### Acceptance Criteria

- trainer 可直接获得统一 dataloader
- batch 中样本格式一致
- label、image、meta 不混乱
- 不需要在训练脚本中手工拼 real/fake 数据

---

## Issue 1-6

### Title
Issue 1-6 — Implement linear probe baseline (B0)

### Background

B0 是 Stage 1 的最小 baseline：frozen encoder + linear probe。  
它的作用不是追求极致性能，而是作为最干净的第一参照，帮助确认：

- baseline backbone 已正确接入
- 数据和训练流程基本正常
- loss 与指标行为合理

### Suggested Branch

`feat/model`

### Goal

实现 B0，并支持通过配置切换运行。

### Scope

- 实现 linear probe head
- 与 frozen encoder 特征接口对接
- 支持 config 中选择 B0
- 对接训练与评估流程

### Deliverables

- linear probe 实现
- B0 配置样例
- 最小训练运行支持

### Acceptance Criteria

- B0 可被独立构建与训练
- 训练过程中无 shape / device / loss 基础错误
- 能输出分类 logits 或概率
- 可进入 train / eval 闭环

---

## Issue 1-7

### Title
Issue 1-7 — Implement MLP probe baseline (B1)

### Background

在 B0 的基础上，B1 作为稍强但仍然简洁的 baseline，用于形成更稳的 Stage 1 对照。  
B1 的引入有两个意义：

- 判断线性 probe 是否过弱
- 为 Stage 2 的 generator-diverse 扩展提供更强起点

### Suggested Branch

`feat/model`

### Goal

实现 B1：frozen encoder + MLP probe，并支持通过配置选择。

### Scope

- 实现 MLP probe head
- 设计最小 hidden 层结构
- 对接 backbone 特征接口
- 对接训练与评估流程
- 与 B0 共用统一 baseline 框架

### Deliverables

- MLP probe 实现
- B1 配置样例
- B1 与 B0 的切换逻辑

### Acceptance Criteria

- B1 可独立构建与训练
- 与 B0 的切换不需要改动训练框架
- 输出接口统一
- 能正常进入 train / eval 闭环

---

## Issue 1-8

### Title
Issue 1-8 — Integrate baseline training loop into current training framework

### Background

Stage 0 的训练脚本骨架已经存在，但 Stage 1 需要把 baseline 真正接入其中。  
这里的重点不是再写一个“临时 baseline_train.py”，而是把 B0/B1 纳入统一训练框架。

### Suggested Branch

`feat/train`

### Goal

将 baseline 的真实训练逻辑接入当前 training framework，使 B0/B1 可通过同一训练入口运行。

### Scope

- 接入 baseline model build
- 接入 unified dataloader
- 构建 loss / optimizer
- 支持 train / val loop
- 支持 best model 保存
- 输出基础训练日志

### Deliverables

- 更新后的训练引擎
- baseline 训练配置
- 最小成功训练记录

### Acceptance Criteria

- B0/B1 均能通过同一训练入口运行
- train / val 行为正常
- best checkpoint 可保存
- 无需额外旁路脚本

---

## Issue 1-9

### Title
Issue 1-9 — Implement baseline evaluation metrics and inference path

### Background

Stage 1 的 baseline 不能只有训练过程，必须尽快形成测试与指标输出闭环。  
这一 issue 的目标是建立 baseline 的正式 eval 路径，而不是只在训练结束后打印临时数值。

### Suggested Branch

`feat/eval`

### Goal

建立 baseline 的推理与评估流程，并输出 Stage 1 所需核心指标。

### Scope

- checkpoint 加载
- test inference
- prediction 收集
- 计算 AUC / Acc
- 可选支持 precision / recall / F1
- 输出 summary 文件

### Deliverables

- baseline evaluator 实现
- AUC / Acc 指标实现
- 评估 summary 输出

### Acceptance Criteria

- 可独立运行 baseline eval
- 至少输出 AUC / Acc
- 结果保存路径规范
- 结果可被 Stage 1 文档或表格引用

---

## Issue 1-10

### Title
Issue 1-10 — Run first-pass baseline experiments and verify training sanity

### Background

在 B0/B1 接入完成后，必须先做 first-pass sanity run，而不是直接追求“最终成绩”。  
这个 issue 的目标是验证：

- loss 是否合理
- 训练是否收敛
- 指标是否具备基本区分能力
- pipeline 是否存在明显 bug

### Suggested Branch

`feat/train`

### Goal

运行 Stage 1 的第一轮 baseline 实验，并完成训练 sanity 检查。

### Scope

- 小规模训练试跑
- B0 first-pass run
- B1 first-pass run
- 检查 train / val 指标行为
- 记录已知问题与异常现象

### Deliverables

- 至少一轮 B0 运行结果
- 至少一轮 B1 运行结果
- sanity check 记录

### Acceptance Criteria

- B0/B1 都有可用 first-pass 结果
- 不存在明显训练逻辑错误
- 可以判断 pipeline 已从“能跑”进入“可实验”

---

## Issue 1-11

### Title
Issue 1-11 — Save checkpoints, prediction summaries, and experiment artifacts

### Background

Stage 1 结束时，必须保证 baseline 结果不是“跑过一次就丢了”，而是可回溯、可复查、可继续扩展。  
因此需要规范化保存实验产物。

### Suggested Branch

`feat/scripts`

### Goal

完善 baseline 实验产物保存逻辑，保证结果可追踪。

### Scope

- 保存 best checkpoint
- 保存 config snapshot
- 保存 prediction summary
- 保存关键日志与指标摘要
- 整理 outputs 结构

### Deliverables

- baseline 输出产物保存逻辑
- 一组完整实验产物示例

### Acceptance Criteria

- 每次 baseline run 都有清晰输出目录
- checkpoint、config、summary 不丢失
- 后续 Stage 2 可直接复用这些产物

---

## Issue 1-12

### Title
Issue 1-12 — Write baseline result table and stage summary

### Background

Milestone 1 的结束不应只是“代码已完成”，还必须有一份清晰的阶段总结，说明：

- 跑了哪些 baseline
- 用了什么配置
- 得到了什么结果
- 当前有哪些已知边界

这份 summary 既服务你自己，也服务后续与导师沟通。

### Suggested Branch

`docs`

### Goal

整理 Stage 1 的 baseline 结果，并形成阶段总结文档。

### Scope

- 汇总 B0 / B1 配置与结果
- 形成简洁结果表
- 记录 Stage 1 的已知问题
- 说明进入 Stage 2 的前提是否满足

### Deliverables

- baseline 结果表
- Stage 1 summary 文档

### Acceptance Criteria

- Stage 1 的结果可被快速理解与复述
- 结果与配置有明确对应关系
- 能清楚判断是否可以进入 Stage 2