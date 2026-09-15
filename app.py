import streamlit as st
import subprocess
import json
from datetime import datetime

st.set_page_config(
    page_title="Fly Agent",
    page_icon="🪰",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🪰 Fly Agent")
st.caption("用果蝇连接组做简单反射反应（原型演示）")

# ==================== 侧边栏 ====================
with st.sidebar:
    st.header("使用说明")
    st.markdown("""
**这是什么？**  
把一句话映射成果蝇的感官刺激，然后看连接组会触发什么反射动作。

**模式说明**  
- **mock**：假脑，速度快，推荐使用  
- **auto**：优先尝试真实脑，失败自动降级  
- **real**：真实 MaleCNS 连接组（云端通常不可用）

**边界提醒**  
这是 reservoir / reflex 原型，不是意识上传，也不是通用 LLM Agent。
    """)
    st.markdown("---")
    st.markdown("[GitHub 项目地址](https://github.com/wyzs6666-bot/fly-agent)")

# ==================== 初始化 ====================
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "history" not in st.session_state:
    st.session_state.history = []

# ==================== 主界面 ====================
col1, col2 = st.columns([3, 1])

with col1:
    # 注意：这里只用 key，不再同时用 value
    text = st.text_input(
        "输入一句话",
        placeholder="例如：一只巨大的手要拍过来",
        key="input_text"          # 关键：key 名称和 session_state 一致
    )

with col2:
    brain = st.selectbox(
        "brain 模式",
        options=["mock", "auto", "real"],
        index=0,
        help="云端强烈建议使用 mock 或 auto"
    )

# ==================== 示例按钮 ====================
st.markdown("**快速试试：**")
examples = [
    "一只巨大的手要拍过来",
    "前面有甜的东西",
    "有危险接近",
    "你好呀",
    "the deadline is going to crash"
]

cols = st.columns(len(examples))
for i, ex in enumerate(examples):
    if cols[i].button(ex, use_container_width=True, key=f"ex_btn_{i}"):
        st.session_state.input_text = ex
        st.rerun()

# ==================== 运行按钮 ====================
run_clicked = st.button("运行", type="primary", use_container_width=True)

if run_clicked and st.session_state.input_text.strip():
    # 简单防刷
    now = datetime.now()
    if "last_run" in st.session_state:
        if (now - st.session_state.last_run).total_seconds() < 1.5:
            st.warning("操作太快，请稍等一下再试")
            st.stop()
    st.session_state.last_run = now

    current_text = st.session_state.input_text.strip()

    with st.spinner("正在运行果蝇反射..."):
        try:
            result = subprocess.run(
                ["fly-agent", "--brain", brain, current_text],
                capture_output=True,
                text=True,
                timeout=45
            )
            output = result.stdout or result.stderr

            try:
                data = json.loads(output)

                # 记录历史
                st.session_state.history.insert(0, {
                    "time": now.strftime("%H:%M:%S"),
                    "input": current_text,
                    "mode": data.get("mode", brain),
                    "data": data
                })
                st.session_state.history = st.session_state.history[:8]

                # ===== 结果展示 =====
                st.success("运行完成")

                actions = data.get("actions", [])
                felt = data.get("felt", "未知")
                sense = data.get("sense", "nothing")

                st.subheader("果蝇的反应")
                if actions:
                    st.info(" → ".join(actions))
                else:
                    st.info("noop（没有明显动作）")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**感觉到：** {felt}")
                with col_b:
                    st.markdown(f"**识别为：** `{sense}`")

                with st.expander("查看详细证据与神经元活动", expanded=False):
                    evidence = data.get("evidence", {})
                    st.json({
                        "extra_spikes": evidence.get("extra_spikes"),
                        "top_descending_neurons": evidence.get("top_descending_neurons"),
                        "reasons": evidence.get("reasons"),
                        "sense_scores": evidence.get("sense_scores"),
                    })

                with st.expander("完整原始结果"):
                    st.json(data)

            except json.JSONDecodeError:
                st.code(output, language="text")
                if "flybrain" in output.lower() or "real brain mode needs" in output.lower():
                    st.error("当前环境不支持 real 模式，请切换到 **mock** 或 **auto** 再试。")

        except subprocess.TimeoutExpired:
            st.error("运行超时，请换 mock 模式重试")
        except Exception as e:
            st.error(f"运行失败：{e}")

# ==================== 历史记录 ====================
if st.session_state.history:
    st.markdown("---")
    st.subheader("最近运行记录")
    for item in st.session_state.history:
        with st.expander(f"{item['time']} | {item['input'][:18]}... | {item['mode']}"):
            data = item["data"]
            st.write("**动作：**", ", ".join(data.get("actions", [])) or "noop")
            st.write("**感觉：**", data.get("felt", ""))
            st.json(data)
