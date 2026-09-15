import streamlit as st
import subprocess
import json

st.set_page_config(page_title="Fly Agent", page_icon="🪰", layout="centered")

st.title("🪰 Fly Agent")
st.caption("用果蝇连接组做简单反射反应（原型演示）")

# 侧边栏说明
with st.sidebar:
    st.header("使用说明")
    st.markdown("""
    **这是什么？**  
    一个极简的果蝇大脑反射 agent。输入一句话，它会映射成感官刺激，再从连接组读出抽象动作。

    **模式说明**  
    - **mock**：假脑，速度快，随时可用  
    - **auto**：自动选择（推荐）  
    - **real**：真实 MaleCNS 连接组（需要本地安装 `flybrain`，云端通常不可用）

    **边界提醒**  
    这是 reservoir/reflex 原型，不是意识上传，也不是通用 LLM agent。
    """)
    st.markdown("---")
    st.markdown("项目地址：[GitHub](https://github.com/wyzs6666-bot/fly-agent)")

# 主界面
col1, col2 = st.columns([3, 1])
with col1:
    text = st.text_input("输入一句话", placeholder="例如：一只巨大的手要拍过来", value="")
with col2:
    brain = st.selectbox("brain 模式", ["mock", "auto", "real"], index=0)

# 示例按钮
st.markdown("**快速试试：**")
examples = [
    "一只巨大的手要拍过来",
    "前面有甜的东西",
    "有危险接近",
    "the deadline is going to crash"
]
cols = st.columns(len(examples))
for i, ex in enumerate(examples):
    if cols[i].button(ex, use_container_width=True):
        text = ex
        st.session_state["example"] = ex
        st.rerun()

if "example" in st.session_state:
    text = st.session_state["example"]

# 运行按钮
if st.button("运行", type="primary", use_container_width=True) and text.strip():
    with st.spinner("正在运行..."):
        try:
            result = subprocess.run(
                ["fly-agent", "--brain", brain, text],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout or result.stderr

            # 尝试解析 JSON
            try:
                data = json.loads(output)
                st.success("运行完成")

                # 美化展示
                if "actions" in data:
                    st.subheader("🧠 动作结果")
                    st.info(", ".join(data["actions"]) if data["actions"] else "noop")

                if "sense" in data or "felt" in data:
                    with st.expander("感官与感受", expanded=True):
                        st.json({k: data.get(k) for k in ["sense", "felt"] if k in data})

                with st.expander("完整原始结果"):
                    st.json(data)

            except json.JSONDecodeError:
                st.code(output, language="text")
                if "flybrain" in output.lower() or "real brain mode needs" in output:
                    st.warning("当前环境不支持 real 模式。请切换到 mock 或 auto 再试。")

        except subprocess.TimeoutExpired:
            st.error("运行超时，请换 mock 模式重试")
        except Exception as e:
            st.error(f"运行失败：{e}")

else:
    st.info("输入一句话后点击「运行」，或直接点上面的示例按钮。")
