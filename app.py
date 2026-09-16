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
if "fly_nonce" not in st.session_state:
    st.session_state.fly_nonce = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_error" not in st.session_state:
    st.session_state.last_error = None

fly_state = st.session_state.fly_state
nonce = st.session_state.fly_nonce

st.markdown(
    f"""
<style>
.stApp {{
  background:
    radial-gradient(1200px 600px at 15% -10%, rgba(120, 190, 230, .35), transparent 55%),
    radial-gradient(900px 500px at 90% 0%, rgba(180, 220, 170, .22), transparent 50%),
    linear-gradient(180deg, #d7ecf8 0%, #eef6fb 42%, #f7f4ee 100%);
}}
[data-testid="stAppViewContainer"] {{
  background: transparent;
}}
[data-testid="stHeader"] {{
  background: transparent;
}}
.stApp::before {{
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: .18;
  background-image:
    linear-gradient(rgba(40,70,90,.18) 1px, transparent 1px),
    linear-gradient(90deg, rgba(40,70,90,.18) 1px, transparent 1px);
  background-size: 28px 28px;
}}
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #1c2a33 0%, #24343e 100%) !important;
}}
[data-testid="stSidebar"] * {{
  color: #e8f0f4 !important;
}}
[data-testid="stSidebar"] a {{
  color: #8fd3ff !important;
}}
.block-container {{
  position: relative;
  z-index: 1;
  background: rgba(255,255,255,.62);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.55);
  border-radius: 18px;
  padding-top: 1.4rem;
  box-shadow: 0 12px 40px rgba(30,50,70,.08);
}}
.stButton > button {{
  border-radius: 10px;
}}

.sky {{
  display: flex;
  justify-content: center;
  align-items: center;
  height: 240px;
  margin: 0 0 4px;
  overflow: visible;
}}
.fly {{
  width: 160px;
  height: 160px;
  position: relative;
  filter: drop-shadow(0 10px 12px rgba(0,0,0,.18));
}}
.fly .ab {{
  width: 36px; height: 58px;
  background: radial-gradient(circle at 30% 20%, #3d4f5f, #1b242c 70%);
  border-radius: 40% 40% 48% 48%;
  position: absolute; left: 62px; top: 62px; z-index: 2;
  box-shadow: inset 0 -8px 0 rgba(0,0,0,.15);
}}
.fly .ab::after {{
  content: "";
  position: absolute; left: 6px; right: 6px; top: 16px;
  height: 28px;
  background: repeating-linear-gradient(
    to bottom,
    transparent 0 6px,
    rgba(0,0,0,.22) 6px 8px
  );
}}
.fly .th {{
  width: 28px; height: 24px;
  background: #24303a;
  border-radius: 50%;
  position: absolute; left: 66px; top: 50px; z-index: 3;
}}
.fly .hd {{
  width: 30px; height: 26px;
  background: #141b21;
  border-radius: 50%;
  position: absolute; left: 65px; top: 30px; z-index: 4;
}}
.fly .eye {{
  width: 11px; height: 11px;
  background: radial-gradient(circle at 35% 30%, #8fd3ff, #2f7fe0 45%, #0b2a4a);
  border-radius: 50%;
  position: absolute; top: 7px;
}}
.fly .eye.l {{ left: 3px; }}
.fly .eye.r {{ right: 3px; }}
.fly .wing {{
  width: 64px; height: 28px;
  background: linear-gradient(180deg, rgba(255,255,255,.55), rgba(210,230,240,.18));
  border: 1px solid rgba(160,180,190,.7);
  border-radius: 70% 70% 50% 50%;
  position: absolute; top: 48px; z-index: 1;
}}
.fly .wing.l {{ left: 12px; transform-origin: 58px 18px; transform: rotate(-18deg); }}
.fly .wing.r {{ right: 12px; transform-origin: 6px 18px; transform: rotate(18deg); }}
.fly .leg {{
  position: absolute; width: 2px; height: 16px;
  background: #1a2228; z-index: 2; border-radius: 1px;
}}
.fly .leg.l1 {{ left: 64px; top: 72px; transform: rotate(25deg); }}
.fly .leg.l2 {{ left: 62px; top: 84px; transform: rotate(12deg); }}
.fly .leg.l3 {{ left: 64px; top: 96px; transform: rotate(-8deg); }}
.fly .leg.r1 {{ right: 64px; top: 72px; transform: rotate(-25deg); }}
.fly .leg.r2 {{ right: 62px; top: 84px; transform: rotate(-12deg); }}
.fly .leg.r3 {{ right: 64px; top: 96px; transform: rotate(8deg); }}

.fly.idle {{ animation: hover 1.8s ease-in-out infinite; }}
.fly.idle .wing.l {{ animation: flapL .16s infinite alternate ease-in-out; }}
.fly.idle .wing.r {{ animation: flapR .16s infinite alternate ease-in-out; }}
.fly.escape {{ animation: escape 1.35s cubic-bezier(.2,.7,.2,1) forwards; }}
.fly.escape .wing.l,
.fly.escape .wing.r {{ animation: flapFast .07s infinite alternate; }}
.fly.approach {{ animation: approach 1.1s ease forwards; }}
.fly.approach .wing.l {{ animation: flapL .22s infinite alternate; }}
.fly.approach .wing.r {{ animation: flapR .22s infinite alternate; }}
.fly.explore {{ animation: explore 2.2s ease-in-out infinite; }}
.fly.explore .wing.l {{ animation: flapL .14s infinite alternate; }}
.fly.explore .wing.r {{ animation: flapR .14s infinite alternate; }}
.fly.noop {{ animation: recoil .55s ease; }}

@keyframes hover {{
  0%,100% {{ transform: translate(0,0) rotate(-2deg); }}
  50% {{ transform: translate(4px,-10px) rotate(2deg); }}
}}
@keyframes flapL {{
  from {{ transform: rotate(-28deg); }}
  to {{ transform: rotate(8deg); }}
}}
@keyframes flapR {{
  from {{ transform: rotate(28deg); }}
  to {{ transform: rotate(-8deg); }}
}}
@keyframes flapFast {{
  from {{ transform: rotate(-38deg); }}
  to {{ transform: rotate(20deg); }}
}}
@keyframes escape {{
  0% {{ transform: translate(0,0) rotate(0) scale(1); opacity: 1; }}
  25% {{ transform: translate(-28px,-36px) rotate(-28deg) scale(1.05); }}
  100% {{ transform: translate(220px,-160px) rotate(48deg) scale(.7); opacity: 0; }}
}}
@keyframes approach {{
  0% {{ transform: translate(0,0) scale(1) rotate(0); }}
  40% {{ transform: translate(0,18px) scale(1.12) rotate(-6deg); }}
  100% {{ transform: translate(0,48px) scale(1.38) rotate(4deg); }}
}}
@keyframes explore {{
  0%,100% {{ transform: translate(0,0) rotate(0); }}
  20% {{ transform: translate(-28px,-16px) rotate(-14deg); }}
  50% {{ transform: translate(6px,-28px) rotate(6deg); }}
  80% {{ transform: translate(30px,-10px) rotate(12deg); }}
}}
@keyframes recoil {{
  0% {{ transform: translate(0,0); }}
  20% {{ transform: translate(-14px,8px) rotate(-12deg); }}
  55% {{ transform: translate(10px,-4px) rotate(8deg); }}
  100% {{ transform: translate(0,0); }}
}}
</style>
<div class="sky">
  <div class="fly {fly_state}" data-n="{nonce}">
    <div class="wing l"></div>
    <div class="wing r"></div>
    <div class="leg l1"></div><div class="leg l2"></div><div class="leg l3"></div>
    <div class="leg r1"></div><div class="leg r2"></div><div class="leg r3"></div>
    <div class="ab"></div>
    <div class="th"></div>
    <div class="hd">
      <div class="eye l"></div>
      <div class="eye r"></div>
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
    sense = str(data.get("sense", "nothing"))
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
                st.session_state.fly_nonce += 1
                st.rerun()
            except json.JSONDecodeError:
                st.session_state.last_result = None
                st.session_state.last_error = output
                st.session_state.fly_state = "noop"
                st.session_state.fly_nonce += 1
                st.rerun()
        except Exception as e:
            st.session_state.last_result = None
            st.session_state.last_error = f"运行失败：{e}"
            st.session_state.fly_state = "noop"
            st.session_state.fly_nonce += 1
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
