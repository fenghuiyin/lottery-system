import streamlit as st
import random
import time
import pandas as pd
import os
from PIL import Image

# ===================== 基础配置 =====================
st.set_page_config(page_title="头像抽奖", layout="wide")
LOTTERY_PASSWORD = "123456"  # 修改你的登录密码

# 【固定抽奖人员名单，不要改动顺序】
member_list = [
    "那刻夏", "啊", "去", "我", "人", "她", "吴",
    "嗯", "二", "发", "给", "就", "看", "被", "那", "吗", "在"
]

# 规则：图片命名规范 → 人名.png
# 举例：那刻夏.png 、啊.png 、我.png
# 所有图片和py文件放在同一个文件夹

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
st.title("🎁 头像在线")
st.divider()

# 刷新候选池：剔除已经中奖的人
win_names = [item["姓名"] for item in st.session_state.winner_history]
st.session_state.candidate_list = [name for name in member_list if name not in win_names]

st.info(f"✅ 当前可参与抽奖人数：{len(st.session_state.candidate_list)} 人")
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

        # ⭐定格展示中奖名单+图片（重点改动区域）
        st.subheader("🎉 中奖名单")
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