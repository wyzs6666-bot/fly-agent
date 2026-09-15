# fly-agent

一个最小可扩展的“果蝇连接组 agent”脚手架。它不是又一个 fly.ai fork 全家桶，而是把边界切开：

- **冻结脑核**：可选依赖 `flybrain`，使用 MaleCNS v1.0 连接组做脉冲网络仿真；脑权重不训练。
- **可替换编码器**：当前 `LexiconSenseEncoder` 只是 bootstrap，把文本映射到少量果蝇感官/特征检测神经元。正式使用时应换成 embedding/图像/环境状态编码器。
- **抽象动作读出**：从 escape/steer/walk/back/groom/wings 等神经元组读出低层行为候选。
- **安全层**：动作白名单 + 上下文守卫；脑输出不能直接产生真实副作用。
- **对照纪律**：任何“有效”的结论都必须过 no-stimulus baseline、degree-preserving scrambled wiring、以及跨 seed 重复。

> 边界提醒：这是 reservoir/reflex core，不是意识上传，也不是已经证明果蝇 wiring 可通用解决 LLM agent 任务。README 级别的上游演示结果不应被视为同行评审结论。

## 快速开始

```bash
cd /mnt/agents/output/fly-agent
python -m pip install -e .[dev]
pytest -q

# 无 brain 数据也能跑接口：
python -m fly_agent.cli --brain mock "the deadline is going to crash"
python -m fly_agent.cli --brain mock --fragile "angry boss attack"
```

真实脑模式：

```bash
python -m pip install -e .[brain]
python -m fly_agent.cli --brain real "a huge hand is going to swat the fly"
# 首次运行会下载约 260 MB 的 MaleCNS brain files；可用 FLY_DATA 指定目录。
```

输出是 JSON，包含 `sense/felt/actions/evidence/brain_log/policy_note`。`actions` 是抽象动作，例如 `jumped`、`turned left`、`noop`；接真实工具前必须经过你自己的 executor 和权限系统。

## 项目结构

```text
fly_agent/
  types.py        # SenseSignal / BrainObservation / AgentResult
  senses.py       # 文本 -> 感官刺激；正式版应替换
  brain_core.py   # FlyBrainCore 真实模式；MockBrainCore 测试模式
  readout.py      # extra spikes -> abstract actions
  safety.py       # 动作白名单与上下文守卫
  agent.py        # 组合 encoder/core/readout/safety
  cli.py          # 最小 CLI
tests/            # mock-mode tests
```

## 下一步建议

1. 把 `LexiconSenseEncoder` 换成可学习或检索式 encoder，但保留 `SenseSignal.stimulated` 可解释字段。
2. 给 `BrainObservation` 增加 scrambled-wiring null control；没有对照，不报告效果。
3. 将 `actions` 接到真实 executor 前，加日志、限速、 dry-run 和人工确认。
4. 若要做成服务，再加 `api` extra 和持久化；不要把脑核放进请求热路径里反复冷启动。

## 许可与署名

代码为 MIT，见 `LICENSE`。上游 `alextitonis/fly.ai` / `flybrain` 的 MIT 与 MaleCNS/Janelia 数据条款见 `NOTICE.md`；使用连接组数据时必须按 Janelia 条款署名和引用。
