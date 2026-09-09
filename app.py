import av
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer

# 別ファイルのモジュールをインポート
from demo1 import OrigamiChecker
from tu import STEPS
import const

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.markdown(const.HIDE_ST_STYLE, unsafe_allow_html=True)

if "step" not in st.session_state:
    st.session_state.step = 1

st_autorefresh(interval=500, key="camera_check")


# =========================================
# VideoProcessor クラス
# =========================================
class VideoProcessor(VideoProcessorBase):

    def __init__(self):
        self.result = False
        self.checker = OrigamiChecker()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # session_stateのステップ番号を引数として渡す
        current_step = st.session_state.get("step", 1)
        self.result, processed_img = self.checker.process_frame(
            img, step=current_step
        )

        return av.VideoFrame.from_ndarray(processed_img, format="bgr24")
# =========================================
# UI レイアウト
# =========================================
cols = st.columns([2, 1], gap="medium")

# --- カメラエリア ---
with cols[0]:
    st.subheader("Camera")
    ctx = webrtc_streamer(
        key="camera",
        video_processor_factory=VideoProcessor,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 1280},
                "height": {"ideal": 720},
                "aspectRatio": {"ideal": 16 / 9},
            },
            "audio": False,
        },
    )

# --- 判定連動 (True時にStep更新) ---
if ctx.video_processor:
    result = getattr(ctx.video_processor, "result", False)

    if result:
        if st.session_state.step <= len(STEPS):
            st.session_state.step += 1
            if st.session_state.step <= len(STEPS):
                st.toast(
                    f"Step {st.session_state.step - 1} クリア！次のステップへ 🎉",
                    icon="🎉",
                )
            else:
                st.toast("すべてのステップが完了しました！ 🎉", icon="🎉")
            st.rerun()

# --- 手順表示エリア (origami.pyと連動) ---
with cols[1]:
    st.subheader("Step")

    current_idx = st.session_state.step - 1

    if current_idx < len(STEPS):
        step_info = STEPS[current_idx]
        st.markdown(f"""
        ### Step {step_info['step']} / {len(STEPS)}
        
        **{step_info['instruction']}**
        
        ---
        💡 *正しく折ってカメラにかざすと自動で次の手順へ進みます。*
        """)
    else:
        st.markdown("""
        ### Complete!
        
        🎉 **Your origami heart is complete!**  
        折り紙のハートが完成しました！
        """)

# --- 下部ステータス ---
st.divider()

if st.session_state.step > len(STEPS):
    st.success("Your origami heart is complete! 🎉")
else:
    st.info(f"現在 Step {st.session_state.step} を実行中です。")
