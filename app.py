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

# ================== 侧边栏 ==================
with st.sidebar:
    st.header("使用说明")
    st.markdown("""
**这是什么？**  
把一句话映射成果蝇的感官刺激，然后看连接组触发什么反射动作。

**模式说明**  
- **mock**：假脑，速度快，推荐使用  
- **auto**：优先尝试真实脑，失败自动降级  
- **real**：真实 MaleCNS 连接组（云端通常不可用）

**边界提醒**  
这是 reservoir / reflex 原型，不是意识上传，也不是通用 LLM Agent。
""")
    st.markdown("---")
    st.markdown("[GitHub 项目地址](https://github.com/wyzs6666-bot/fly-agent)")

# ================== 初始化 ==================
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "fly_state" not in st.session_state:
    st.session_state.fly_state = "idle"

# ================== 果蝇动画 HTML ==================
fly_html = f"""
<div id="fly-container" style="position:fixed; bottom:30px; right:30px; width:100px; height:100px; z-index:9999; pointer-events:none;">
  <div class="fly {st.session_state.fly_state}" id="fly">
    <div class="wing left"></div>
    <div class="wing right"></div>
    <div class="body"></div>
    <div class="head">
      <div class="eye left"></div>
      <div class="eye right"></div>
    </div>
  </div>
</div>

<style>
  .fly {{
    width: 70px;
    height: 70px;
    position: relative;
    transition: transform 0.4s ease;
  }}
  .body {{
    width: 24px;
    height: 34px;
    background: #2c3e50;
    border-radius: 50% 50% 40% 40%;
    position: absolute;
    left: 23px;
    top: 18px;
    z-index: 2;
  }}
  .head {{
    width: 20px;
    height: 20px;
    background: #1a252f;
    border-radius: 50%;
    position: absolute;
    left: 25px;
    top: 4px;
    z-index: 3;
  }}
  .eye {{
    width: 6px;
    height: 6px;
    background: #e74c3c;
    border-radius: 50%;
    position: absolute;
    top: 5px;
  }}
  .eye.left {{ left: 2px; }}
  .eye.right {{ right: 2px; }}
  .wing {{
    width: 32px;
    height: 16px;
    background: rgba(255,255,255,0.75);
    border: 1px solid #bbb;
    border-radius: 50%;
    position: absolute;
    top: 16px;
    z-index: 1;
    transform-origin: left center;
  }}
  .wing.left {{
    left: 6px;
    transform: rotate(-15deg);
  }}
  .wing.right {{
    right: 6px;
    transform: rotate(15deg) scaleX(-1);
  }}

  .fly.idle .wing.left {{
    animation: flap-left 0.3s infinite alternate ease-in-out;
  }}
  .fly.idle .wing.right {{
    animation: flap-right 0.3s infinite alternate ease-in-out;
  }}
  .fly.escape {{
    animation: escape-fly 1.3s forwards;
  }}
  .fly.escape .wing.left,
  .fly.escape .wing.right {{
    animation: flap-fast 0.08s infinite alternate;
  }}
  .fly.approach {{
    animation: approach 1s forwards;
  }}
  .fly.explore {{
    animation: explore 1.6s infinite;
  }}

  @keyframes flap-left {{
    from {{ transform: rotate(-20deg); }}
    to   {{ transform: rotate(10deg); }}
  }}
  @keyframes flap-right {{
    from {{ transform: rotate(20deg) scaleX(-1); }}
    to   {{ transform: rotate(-10deg) scaleX(-1); }}
  }}
  @keyframes flap-fast {{
    from {{ transform: rotate(-30deg); }}
    to   {{ transform: rotate(25deg); }}
  }}
  @keyframes escape-fly {{
    0%   {{ transform: translate(0, 0) rotate(0deg); opacity: 1; }}
    40%  {{ transform: translate(-40px, -50px) rotate(-25deg); }}
    100% {{ transform: translate(180px, -280px) rotate(45deg); opacity: 0; }}
  }}
  @keyframes approach {{
    0%   {{ transform: translate(0, 0) scale(1); }}
    100% {{ transform: translate(-50px, -25px) scale(1.2); }}
  }}
  @keyframes explore {{
    0%, 100% {{ transform: translate(0, 0) rotate(0deg); }}
    25%      {{ transform: translate(-12px, -8px) rotate(-6deg); }}
    75%      {{ transform: translate(12px, -4px) rotate(6deg); }}
  }}
</style>
"""

st.components.v1.html(fly_html, height=0)

# ================== 主界面 ==================
col1, col2 = st.columns([3, 1])
with col1:
    text = st.text_input("输入一句话", value=st.session_state.input_text, placeholder="例如：一只巨大的手要拍过来")
with col2:
    brain = st.selectbox("brain 模式", ["mock", "auto", "real"], index=0)

# 快速试试
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
    if cols[i].button(ex, use_container_width=True):
        st.session_state.input_text = ex
        st.rerun()

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

            try:
                data = json.loads(output)
                st.success("运行完成")

                # 根据结果切换果蝇状态
                sense = data.get("sense", "nothing")
                actions = data.get("actions", [])
                felt = data.get("felt", "")

                if sense == "threat" or "jumped" in actions or "危险" in felt or "手" in text:
                    st.session_state.fly_state = "escape"
                elif sense == "taste" or "甜" in felt:
                    st.session_state.fly_state = "approach"
                elif sense == "mate" or "你好" in text:
                    st.session_state.fly_state = "explore"
                else:
                    st.session_state.fly_state = "idle"

                # 显示结果
                st.subheader("果蝇的反应")
                action_text = ", ".join(actions) if actions else "noop"
                st.info(action_text)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**感觉到：** {felt}")
                with col_b:
                    st.markdown(f"**识别为：** `{sense}`")

                with st.expander("查看详细证据与神经元活动"):
                    st.json(data.get("evidence", {}))

                with st.expander("完整原始结果"):
                    st.json(data)

                # 强制刷新动画
                st.rerun()

            except json.JSONDecodeError:
                st.code(output, language="text")
                if "flybrain" in output.lower() or "real brain mode needs" in output:
                    st.warning("当前环境不支持 real 模式，请切换到 mock 或 auto 再试。")

        except subprocess.TimeoutExpired:
            st.error("运行超时，请换 mock 模式重试")
        except Exception as e:
            st.error(f"运行失败：{e}")

else:
    st.info("输入一句话后点击「运行」，或直接点上面的示例按钮。")
