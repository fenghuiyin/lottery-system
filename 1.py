import streamlit as st
import random
import time
import pandas as pd
import os
from PIL import Image
import base64


# ===================== 背景图片函数 =====================
def set_bg_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    base64_str = base64.b64encode(data).decode()
    bg_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{base64_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.4);
        z-index: 0;
    }}
    .stApp > div {{
        position: relative;
        z-index: 1;
    }}
    </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)


# ===================== 基础配置 =====================
st.set_page_config(page_title="头像在线抽奖", layout="wide")
# 开启背景，把背景图片bg.png和代码放在同一目录
set_bg_image("bg.png")

# 从云端密钥读取密码（不要明文写在代码里）
LOTTERY_PASSWORD = st.secrets["PASSWORD"]

# 【固定抽奖人员名单，不要改动顺序】
member_list = [
    "那刻夏", "啊", "去", "我", "人", "她", "吴",
    "嗯", "二", "发", "给", "就", "看", "被", "那", "吗", "在"
]

# 款式规则
bath_towel_name = "那刻夏"  # 澡巾款
# 普通款 = 名单中除那刻夏以外所有人

# 初始化会话变量
if "login_ok" not in st.session_state:
    st.session_state.login_ok = False
if "candidate_list" not in st.session_state:
    st.session_state.candidate_list = member_list.copy()
if "winner_history" not in st.session_state:
    st.session_state.winner_history = []
if "rolling_name" not in st.session_state:
    st.session_state.rolling_name = "等待抽奖"
if "final_winners" not in st.session_state:
    st.session_state.final_winners = []

# ===================== 密码登录页面 =====================
if not st.session_state.login_ok:
    st.title("🔐 头像抽奖")
    input_pwd = st.text_input("请输入抽奖密码", type="password")
    if st.button("登录系统"):
        if input_pwd == LOTTERY_PASSWORD:
            st.session_state.login_ok = True
            st.rerun()
        else:
            st.error("密码错误！")
    st.stop()

# ===================== 主页面 =====================
st.title("🎁 头像在线抽奖")
st.divider()

# 刷新候选池：剔除已经中奖的人
win_names = [item["姓名"] for item in st.session_state.winner_history]
st.session_state.candidate_list = [name for name in member_list if name not in win_names]

# 拆分剩余候选：普通款 / 澡巾款
remain_all = st.session_state.candidate_list
remain_bath_towel = [x for x in remain_all if x == bath_towel_name]
remain_normal = [x for x in remain_all if x != bath_towel_name]

st.info(f"✅ 当前可参与抽奖总人数：{len(remain_all)} 人")
# ========== 新增：显示两类款式剩余数量 ==========
st.success(f"🧴 剩余普通款人数：{len(remain_normal)} 人")
st.warning(f"🛁 剩余澡巾款人数：{len(remain_bath_towel)} 人")

st.header(f"滚动名单：{st.session_state.rolling_name}")

pick_num = st.number_input("单次抽取人数", min_value=1, value=1)

if st.button("🔥 开始抽奖", type="primary", use_container_width=True):
    candidates = st.session_state.candidate_list
    if len(candidates) == 0:
        st.warning("所有人已经中奖完毕！")
    elif pick_num > len(candidates):
        st.error(f"抽取人数不能大于剩余{len(candidates)}人！")
    else:
        # 滚动动画区域
        anim_place = st.empty()
        for _ in range(40):
            random_name = random.choice(candidates)
            st.session_state.rolling_name = random_name
            anim_place.header(f"🎲 滚动中：{random_name}")
            time.sleep(0.07)
        anim_place.empty()

        # 选出中奖者
        lucky_people = random.sample(candidates, k=pick_num)
        st.session_state.rolling_name = "抽奖结束"
        # 保存中奖名单，定格展示
        st.session_state.final_winners = lucky_people.copy()

        # 保存到历史记录
        for name in lucky_people:
            st.session_state.winner_history.append({"姓名": name})

        # 定格展示中奖名单+图片
        st.subheader("🎉 中奖名单")
        for name in st.session_state.final_winners:
            st.success(f"恭喜：{name}")
            img_path = f"{name}.png"
            if os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(img, width=350, caption=name)
            else:
                st.warning(f"未找到图片：{name}.png，请检查文件！")

st.divider()
# 历史中奖记录
st.subheader("📋 全部中奖记录")
if st.session_state.winner_history:
    df = pd.DataFrame(st.session_state.winner_history)
    st.dataframe(df, use_container_width=True)
    csv_text = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("下载中奖记录csv", data=csv_text, file_name="中奖名单.csv")
    if st.button("重置所有中奖记录"):
        st.session_state.winner_history.clear()
        st.session_state.final_winners.clear()
        st.rerun()
else:
    st.info("暂无中奖记录")