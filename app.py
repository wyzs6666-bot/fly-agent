import streamlit as st
import subprocess
import json

st.set_page_config(
    page_title="Fly Agent",
    page_icon="🪰",
    layout="centered",
    initial_sidebar_state="expanded",
)

if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "fly_state" not in st.session_state:
    st.session_state.fly_state = "idle"
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_error" not in st.session_state:
    st.session_state.last_error = None

fly_state = st.session_state.fly_state

st.markdown(
    f"""
<style>
.sky {{
  display: flex;
  justify-content: center;
  align-items: flex-end;
  height: 140px;
  margin: 0 0 8px;
}}
.fly {{
  width: 78px;
  height: 78px;
  position: relative;
}}
.body {{
  width: 24px; height: 34px;
  background: #2c3e50;
  border-radius: 50% 50% 40% 40%;
  position: absolute; left: 27px; top: 22px; z-index: 2;
}}
.head {{
  width: 20px; height: 20px;
  background: #1a252f; border-radius: 50%;
  position: absolute; left: 29px; top: 6px; z-index: 3;
}}
.eye {{
  width: 6px; height: 6px;
  background: #5ab0ff; border-radius: 50%;
  position: absolute; top: 6px;
}}
.eye.left {{ left: 2px; }}
.eye.right {{ right: 2px; }}
.wing {{
  width: 32px; height: 16px;
  background: rgba(255,255,255,.8);
  border: 1px solid #bbb; border-radius: 50%;
  position: absolute; top: 18px; z-index: 1;
}}
.wing.left {{ left: 6px; transform: rotate(-15deg); transform-origin: right center; }}
.wing.right {{ right: 6px; transform: rotate(15deg); transform-origin: left center; }}
.fly.idle .wing.left {{ animation: flapL .28s infinite alternate ease-in-out; }}
.fly.idle .wing.right {{ animation: flapR .28s infinite alternate ease-in-out; }}
.fly.escape {{ animation: escapeFly 1.25s forwards; }}
.fly.escape .wing.left,
.fly.escape .wing.right {{ animation: flapFast .08s infinite alternate; }}
.fly.approach {{ animation: approach 1s forwards; }}
.fly.explore {{ animation: explore 1.6s infinite; }}
.fly.noop {{ animation: shake .4s ease; }}
@keyframes flapL {{ from {{ transform: rotate(-22deg); }} to {{ transform: rotate(8deg); }} }}
@keyframes flapR {{ from {{ transform: rotate(22deg); }} to {{ transform: rotate(-8deg); }} }}
@keyframes flapFast {{ from {{ transform: rotate(-28deg); }} to {{ transform: rotate(22deg); }} }}
@keyframes escapeFly {{
  0% {{ transform: translate(0,0) rotate(0); opacity: 1; }}
  100% {{ transform: translate(160px,-90px) rotate(40deg); opacity: 0; }}
}}
@keyframes approach {{
  0% {{ transform: translate(0,0) scale(1); }}
  100% {{ transform: translate(0,16px) scale(1.18); }}
}}
@keyframes explore {{
  0%,100% {{ transform: translate(0,0); }}
  25% {{ transform: translate(-14px,-8px) rotate(-8deg); }}
  75% {{ transform: translate(14px,-6px) rotate(8deg); }}
}}
@keyframes shake {{
  0%,100% {{ transform: translateX(0); }}
  30% {{ transform: translateX(-7px); }}
  60% {{ transform: translateX(7px); }}
}}
</style>
<div class="sky">
  <div class="fly {fly_state}">
    <div class="wing left"></div>
    <div class="wing right"></div>
    <div class="body"></div>
    <div class="head">
      <div class="eye left"></div>
      <div class="eye right"></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.title("🪰 Fly Agent")
st.caption("用果蝇连接组做简单反射反应（原型演示）")

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

col1, col2 = st.columns([3, 1])
with col1:
    text = st.text_input(
        "输入一句话",
        value=st.session_state.input_text,
        placeholder="例如：一只巨大的手要拍过来",
    )
    st.session_state.input_text = text
with col2:
    brain = st.selectbox("brain 模式", ["mock", "auto", "real"], index=0)

st.markdown("**快速试试：**")
examples = [
    "一只巨大的手要拍过来",
    "前面有甜的东西",
    "有危险接近",
    "你好呀",
    "the deadline is going to crash",
]
cols = st.columns(len(examples))
for i, ex in enumerate(examples):
    if cols[i].button(ex, use_container_width=True, key=f"btn_{i}"):
        st.session_state.input_text = ex
        st.rerun()

def pick_fly_state(data, raw):
    sense = data.get("sense", "nothing")
    actions = data.get("actions", []) or []
    felt = str(data.get("felt", ""))
    if sense == "threat" or "jumped" in str(actions) or "危险" in felt or "手" in raw:
        return "escape"
    if sense == "taste" or "甜" in felt:
        return "approach"
    if sense == "mate" or "你好" in raw:
        return "explore"
    if not actions or actions == ["noop"]:
        return "noop"
    return "idle"

if st.button("运行", type="primary", use_container_width=True) and st.session_state.input_text.strip():
    with st.spinner("正在运行..."):
        try:
            result = subprocess.run(
                ["fly-agent", "--brain", brain, st.session_state.input_text],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout or result.stderr
            try:
                data = json.loads(output)
                st.session_state.last_result = data
                st.session_state.last_error = None
                st.session_state.fly_state = pick_fly_state(data, st.session_state.input_text)
                st.rerun()
            except json.JSONDecodeError:
                st.session_state.last_result = None
                st.session_state.last_error = output
                st.session_state.fly_state = "noop"
                st.rerun()
        except Exception as e:
            st.session_state.last_result = None
            st.session_state.last_error = f"运行失败：{e}"
            st.session_state.fly_state = "noop"
            st.rerun()

data = st.session_state.last_result
err = st.session_state.last_error

if data:
    st.success("运行完成")
    st.subheader("果蝇的反应")
    actions = data.get("actions", []) or []
    st.info(", ".join(actions) if actions else "noop")
    c1, c2 = st.columns(2)
    c1.markdown(f"**感觉到：** {data.get('felt', '')}")
    c2.markdown(f"**识别为：** `{data.get('sense', '')}`")
    with st.expander("查看详细证据与神经元活动"):
        st.json(data.get("evidence", {}))
    with st.expander("完整原始结果"):
        st.json(data)
elif err:
    st.code(err)
    if "flybrain" in str(err).lower():
        st.warning("当前环境不支持 real 模式，请用 mock 或 auto")
else:
    st.info("输入一句话后点击「运行」，或直接点上面的示例按钮。")
