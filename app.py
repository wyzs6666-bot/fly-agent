import streamlit as st
import streamlit.components.v1 as components
import subprocess
import json

st.set_page_config(
    page_title="Fly Agent",
    page_icon="🪰",
    layout="centered",
    initial_sidebar_state="expanded",
)

components.html(
    """
    <script>
    const doc = window.parent.document;

    const styleId = "x-link-style";
    let style = doc.getElementById(styleId);
    if (!style) {
      style = doc.createElement("style");
      style.id = styleId;
      doc.head.appendChild(style);
    }
    style.textContent = `
      [data-testid="stHeader"] {
        pointer-events: none !important;
        background: transparent !important;
      }
      [data-testid="stToolbar"] {
        pointer-events: auto !important;
      }
      .x-fixed-link {
        position: fixed !important;
        top: 18px !important;
        right: 230px !important;
        z-index: 2147483647 !important;
        pointer-events: auto !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        color: #e8f0f4 !important;
        text-decoration: none !important;
        font-family: sans-serif !important;
        cursor: pointer !important;
      }
      [data-testid="stSidebarCollapsedControl"],
      [data-testid="collapsedControl"],
      [data-testid="stExpandSidebarButton"] {
        pointer-events: auto !important;
        background: rgba(255,255,255,.22) !important;
        border: 1px solid #ffffff !important;
        color: #ffffff !important;
        box-shadow: 0 0 12px rgba(255,255,255,.4) !important;
      }
      [data-testid="stSidebarCollapsedControl"] svg,
      [data-testid="collapsedControl"] svg,
      [data-testid="stExpandSidebarButton"] svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
      }
    `;

    let a = doc.querySelector(".x-fixed-link");
    if (!a) {
      a = doc.createElement("a");
      a.className = "x-fixed-link";
      doc.body.appendChild(a);
    }
    a.href = "https://x.com/BSC_FlyAgent";
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.textContent = "𝕏";

    function openSidebar() {
      const btn = doc.querySelector('[data-testid="stSidebarCollapsedControl"]')
        || doc.querySelector('[data-testid="collapsedControl"]')
        || doc.querySelector('[data-testid="stExpandSidebarButton"]');
      if (btn) btn.click();
    }
    openSidebar();
    setTimeout(openSidebar, 200);
    setTimeout(openSidebar, 600);
    setTimeout(openSidebar, 1200);
    </script>
    """,
    height=0,
)

CA = "0xb6f61aab7a9f5c2bcf8dd2c87bdfeb7225547777"
BSCSCAN = f"https://bscscan.com/token/{CA}"

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
if "lang" not in st.session_state:
    st.session_state.lang = "zh"

T = {
    "zh": {
        "caption": "用果蝇连接组做简单反射反应（原型演示）",
        "sidebar_title": "使用说明",
        "sidebar_body": """
**这是什么？**  
把一句话映射成果蝇的感官刺激，然后看连接组触发什么反射动作。

**模式说明**  
- **mock**：假脑，速度快，推荐使用  
- **auto**：优先尝试真实脑，失败自动降级  
- **real**：真实 MaleCNS 连接组（云端通常不可用）

**边界提醒**  
这是 reservoir / reflex 原型，不是意识上传，也不是通用 LLM Agent。
""",
        "github": "GitHub 项目地址",
        "ca_label": "合约地址 CA (BSC)",
        "ca_link": "在 BscScan 查看",
        "input": "输入一句话",
        "placeholder": "例如：一只巨大的手要拍过来",
        "brain": "brain 模式",
        "try": "快速试试：",
        "run": "运行",
        "running": "正在运行...",
        "done": "运行完成",
        "reaction": "果蝇的反应",
        "felt": "感觉到：",
        "sense": "识别为：",
        "evidence": "查看详细证据与神经元活动",
        "raw": "完整原始结果",
        "fail": "运行失败：",
        "real_warn": "当前环境不支持 real 模式，请用 mock 或 auto",
        "hint": "输入一句话后点击「运行」，或直接点上面的示例按钮。",
        "examples": [
            "一只巨大的手要拍过来",
            "前面有甜的东西",
            "有危险接近",
            "你好呀",
            "the deadline is going to crash",
        ],
    },
    "en": {
        "caption": "Simple reflex demo using the fly connectome",
        "sidebar_title": "How to use",
        "sidebar_body": """
**What is this?**  
Map a sentence to fly sensory input, then see which reflex the connectome fires.

**Modes**  
- **mock**: fake brain, fast, recommended  
- **auto**: try the real brain first, fall back if it fails  
- **real**: real MaleCNS connectome (usually unavailable in the cloud)

**Limits**  
This is a reservoir / reflex prototype, not mind uploading, and not a general LLM agent.
""",
        "github": "GitHub repo",
        "ca_label": "Contract Address CA (BSC)",
        "ca_link": "View on BscScan",
        "input": "Enter a sentence",
        "placeholder": "e.g. A giant hand is about to slap",
        "brain": "brain mode",
        "try": "Try these:",
        "run": "Run",
        "running": "Running...",
        "done": "Done",
        "reaction": "Fly response",
        "felt": "Felt:",
        "sense": "Classified as:",
        "evidence": "Evidence and neuron activity",
        "raw": "Full raw result",
        "fail": "Failed: ",
        "real_warn": "Real mode is not supported here. Use mock or auto.",
        "hint": "Type a sentence and click Run, or use an example button above.",
        "examples": [
            "A giant hand is about to slap",
            "Something sweet ahead",
            "Danger approaching",
            "Hello there",
            "the deadline is going to crash",
        ],
    },
}

def _set_lang():
    st.session_state.lang = "zh" if st.session_state.lang_radio == "中文" else "en"

t = T[st.session_state.lang]

fly_state = st.session_state.fly_state
nonce = st.session_state.fly_nonce

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
  font-family: "IBM Plex Sans", "Noto Sans SC", sans-serif;
}}

.stApp {{
  background:
    radial-gradient(900px 520px at 12% -8%, rgba(47,127,224,.28), transparent 58%),
    radial-gradient(700px 420px at 92% 8%, rgba(143,211,255,.12), transparent 52%),
    radial-gradient(800px 600px at 50% 110%, rgba(212,160,80,.10), transparent 55%),
    linear-gradient(180deg, #0b1218 0%, #101920 46%, #16110c 100%);
  color: #e8f0f4;
}}
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {{
  background: transparent;
}}

.stApp::before {{
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: .22;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='98' viewBox='0 0 56 98'%3E%3Cpath d='M28 2 L54 17 V47 L28 62 L2 47 V17 Z' fill='none' stroke='%238fd3ff' stroke-width='1'/%3E%3C/svg%3E");
  background-size: 56px 98px;
  mask-image: radial-gradient(ellipse at 50% 30%, black 20%, transparent 75%);
}}

.stApp::after {{
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    radial-gradient(circle at 18% 22%, rgba(143,211,255,.55) 0 1.2px, transparent 1.8px),
    radial-gradient(circle at 72% 18%, rgba(47,127,224,.5) 0 1px, transparent 1.6px),
    radial-gradient(circle at 40% 70%, rgba(143,211,255,.35) 0 1px, transparent 1.6px),
    radial-gradient(circle at 86% 64%, rgba(212,160,80,.4) 0 1.2px, transparent 1.8px);
}}

[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #0a1116 0%, #132028 100%) !important;
  border-right: 1px solid rgba(143,211,255,.12);
}}
[data-testid="stSidebar"] * {{
  color: #d7e6ee !important;
}}
[data-testid="stSidebar"] a {{
  color: #8fd3ff !important;
}}

.block-container {{
  position: relative;
  z-index: 1;
  background:
    linear-gradient(180deg, rgba(16,28,36,.86), rgba(12,20,26,.78));
  backdrop-filter: blur(14px);
  border: 1px solid rgba(143,211,255,.16);
  border-radius: 22px;
  padding-top: 1.2rem;
  box-shadow:
    0 0 0 1px rgba(0,0,0,.35),
    0 24px 60px rgba(0,0,0,.35),
    inset 0 1px 0 rgba(255,255,255,.06);
}}

h1, h2, h3, .stMarkdown, .stCaption, label, p {{
  color: #e8f0f4 !important;
}}
.stCaption, [data-testid="stCaptionContainer"] {{
  color: #9bb3c0 !important;
}}

.stTextInput input, .stSelectbox [data-baseweb="select"] > div {{
  background: rgba(8,14,18,.72) !important;
  color: #e8f0f4 !important;
  border: 1px solid rgba(143,211,255,.22) !important;
  border-radius: 12px !important;
}}

.stButton > button {{
  border-radius: 12px;
  border: 1px solid rgba(143,211,255,.18);
  background: rgba(20,32,40,.7);
  color: #e8f0f4;
}}
.stButton > button[kind="primary"] {{
  background: linear-gradient(90deg, #1e5dad, #2f7fe0) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 8px 24px rgba(47,127,224,.35);
}}

div[data-testid="stAlert"] {{
  border-radius: 12px;
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
  filter: drop-shadow(0 10px 18px rgba(0,0,0,.45)) drop-shadow(0 0 18px rgba(47,127,224,.25));
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
  box-shadow: 0 0 8px rgba(143,211,255,.7);
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
st.caption(t["caption"])
st.caption(f"CA: `{CA}`")
st.radio(
    "Language / 语言",
    ["中文", "English"],
    index=0 if st.session_state.lang == "zh" else 1,
    horizontal=True,
    key="lang_radio",
    on_change=_set_lang,
)
t = T[st.session_state.lang]

with st.sidebar:
    st.header(t["sidebar_title"])
    st.markdown(t["sidebar_body"])
    st.markdown("---")
    st.markdown(f"**{t['ca_label']}**")
    st.code(CA, language=None)
    st.markdown(f"[{t['ca_link']}]({BSCSCAN})")
    st.markdown("---")
    st.markdown(f"[{t['github']}](https://github.com/wyzs6666-bot/fly-agent)")
    st.markdown("[𝕏 @BSC_FlyAgent](https://x.com/BSC_FlyAgent)")

col1, col2 = st.columns([3, 1])
with col1:
    text = st.text_input(
        t["input"],
        value=st.session_state.input_text,
        placeholder=t["placeholder"],
    )
    st.session_state.input_text = text
with col2:
    brain = st.selectbox(t["brain"], ["mock", "auto", "real"], index=0)

st.markdown(f"**{t['try']}**")
examples = t["examples"]
cols = st.columns(len(examples))
for i, ex in enumerate(examples):
    if cols[i].button(ex, use_container_width=True, key=f"btn_{i}"):
        st.session_state.input_text = ex
        st.rerun()

def pick_fly_state(data, raw):
    sense = str(data.get("sense", "nothing"))
    actions = data.get("actions", []) or []
    felt = str(data.get("felt", ""))
    raw_l = raw.lower()
    if (
        sense == "threat"
        or "jumped" in str(actions)
        or "危险" in felt
        or "手" in raw
        or "danger" in raw_l
        or "slap" in raw_l
        or "hand" in raw_l
    ):
        return "escape"
    if sense == "taste" or "甜" in felt or "sweet" in raw_l:
        return "approach"
    if sense == "mate" or "你好" in raw or "hello" in raw_l:
        return "explore"
    if not actions or actions == ["noop"]:
        return "noop"
    return "idle"

if st.button(t["run"], type="primary", use_container_width=True) and st.session_state.input_text.strip():
    with st.spinner(t["running"]):
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
            st.session_state.last_error = f"{t['fail']}{e}"
            st.session_state.fly_state = "noop"
            st.session_state.fly_nonce += 1
            st.rerun()

data = st.session_state.last_result
err = st.session_state.last_error

if data:
    st.success(t["done"])
    st.subheader(t["reaction"])
    actions = data.get("actions", []) or []
    st.info(", ".join(actions) if actions else "noop")
    c1, c2 = st.columns(2)
    c1.markdown(f"**{t['felt']}** {data.get('felt', '')}")
    c2.markdown(f"**{t['sense']}** `{data.get('sense', '')}`")
    with st.expander(t["evidence"]):
        st.json(data.get("evidence", {}))
    with st.expander(t["raw"]):
        st.json(data)
elif err:
    st.code(err)
    if "flybrain" in str(err).lower():
        st.warning(t["real_warn"])
else:
    st.info(t["hint"])
