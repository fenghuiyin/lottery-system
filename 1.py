import streamlit as st
import random
import time
import pandas as pd
import os
from PIL import Image
import base64

# ===================== 基础配置 =====================
st.set_page_config(page_title="无料抽奖系统", layout="wide")

# 函数：读取本地图片转为base64
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
    /* 半透明遮罩，防止文字看不清，可自行调整透明度 0~1 */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(225, 225, 225, 0.6);
        z-index: 0;
    }}
    .stApp > div {{
        position: relative;
        z-index: 1;
    }}
    </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)

# ===================== 配置页面 =====================
# 调用函数，填入你的背景图片文件名（和1.py同目录）
set_bg_image("bg.png")
LOTTERY_PASSWORD = "123456"  # 修改你的登录密码

# 【固定抽奖人员名单，不要改动顺序】
member_list = [
    "阿那克萨戈拉斯", "缇宝", "阿格莱雅", "万敌", "白厄", "风堇", "海瑟音",
    "遐蝶", "刻律德拉", "丹恒*腾荒","赛飞儿", "昔涟", "长夜月", "丹恒", "三月七", "开拓者", "星期日"
]
# 款式定义：只有【长夜月】是澡巾款
bath_towel_person = "长夜月"

# 初始化会话变量
if "login_ok" not in st.session_state:
    st.session_state.login_ok = False
if "candidate_list" not in st.session_state:
    st.session_state.candidate_list = member_list.copy()
if "winner_history" not in st.session_state:
    st.session_state.winner_history = []
if "rolling_name" not in st.session_state:
    st.session_state.rolling_name = "等待抽奖"
# 新增：保存最终中奖名单，用于定格展示
if "final_winners" not in st.session_state:
    st.session_state.final_winners = []

# ===================== 密码登录页面 =====================
if not st.session_state.login_ok:
    st.title("🎁 无料抽奖系统")
    input_pwd = st.text_input("请输入抽奖密码", type="password")
    if st.button("登录系统"):
        if input_pwd == LOTTERY_PASSWORD:
            st.session_state.login_ok = True
            st.rerun()
        else:
            st.error("密码错误！")
    st.stop()

# ===================== 主页面 =====================
st.title("🎁 无料在线抽奖")
st.divider()

# 刷新候选池：剔除已经中奖的人
win_names = [item["姓名"] for item in st.session_state.winner_history]
st.session_state.candidate_list = [name for name in member_list if name not in win_names]

remain_all = st.session_state.candidate_list
remain_bath_towel = [name for name in remain_all if name == bath_towel_person]
remain_normal = [name for name in remain_all if name != bath_towel_person]

st.info(f"✅ 当前剩余无料数量：{len(st.session_state.candidate_list)} 人")
# =========新增两行款式剩余数量显示，位置在总人数下方=========
st.success(f"🧴 剩余普通款数量：{len(remain_normal)} 人")
st.warning(f"⭐ 剩余澡巾款数量：{len(remain_bath_towel)} 人")

st.header(f"滚动名单：{st.session_state.rolling_name}")

pick_num = st.number_input("单次抽取人数", min_value=1, value=1)

if st.button("🔥 开始抽奖", type="primary", use_container_width=True):
    candidates = st.session_state.candidate_list
    if len(candidates) == 0:
        st.warning("所有无料已经发放完毕！")
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

        # ⭐定格展示中奖名单+图片（重点改动区域）
        st.subheader("🎉 所出无料角色")
        for name in st.session_state.final_winners:
            st.success(f"恭喜：{name}")
            img_path = f"{name}.png"
            if os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(img, width=350, caption=name)
            else:
                st.warning(f"未找到图片：{name}.png，请检查文件！")

        # 移除自动刷新！！取消 st.rerun()
        # 取消自动刷新，页面定格在中奖画面

st.divider()
# 历史中奖记录
st.subheader("📋 所出无料记录")
if st.session_state.winner_history:
    df = pd.DataFrame(st.session_state.winner_history)
    st.dataframe(df, use_container_width=True)
    csv_text = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("下载所出无料记录csv", data=csv_text, file_name="所出无料名单.csv")
    if st.button("重置所有无料记录"):
        st.session_state.winner_history.clear()
        st.session_state.final_winners.clear()
        st.rerun()
else:
    st.info("暂无抽取记录")