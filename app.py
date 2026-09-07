import av
import streamlit as st
from streamlit_webrtc import (
    webrtc_streamer,
    VideoProcessorBase,
)
from streamlit_autorefresh import st_autorefresh
import const

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    const.HIDE_ST_STYLE,
    unsafe_allow_html=True
)

if "step" not in st.session_state:
    st.session_state.step = 1

st_autorefresh(
    interval=500,
    key="camera_check"
)

def image_processing(img):
    """
    テスト用。

    カメラから5フレーム受け取ったらTrue。
    """

    return True

class VideoProcessor(VideoProcessorBase):

    def __init__(self):
        self.result = False
        self.count = 0

    def recv(self, frame):

        # カメラ映像をOpenCV形式に変換
        img = frame.to_ndarray(format="bgr24")

        # フレーム数をカウント
        self.count += 1

        # =========================
        # 画像処理
        # =========================

        if self.count >= 5:
            self.result = True

        # =========================
        # カメラ映像をそのまま表示
        # =========================

        return av.VideoFrame.from_ndarray(
            img,
            format="bgr24"
        )


# =========================
# メイン
# =========================

cols = st.columns(
    [2, 1],
    gap="medium"
)


# =========================
# Camera
# =========================

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


# =========================
# 画像処理結果の確認
# =========================

if ctx.video_processor:

    result = getattr(
        ctx.video_processor,
        "result",
        False
    )

    if result:

        # Stepを進める
        if st.session_state.step < 3:

            st.session_state.step += 1

            st.toast(
                "素晴らしい！次のステップへ 🎉",
                icon="🎉"
            )

            st.rerun()


# =========================
# Step
# =========================

with cols[1]:

    st.subheader("Step")

    if st.session_state.step == 1:

        st.markdown("""
        ### 手順1

        カメラを対象に向けてください。

        **対象を検出すると次の手順へ進みます。**
        """)

    elif st.session_state.step == 2:

        st.markdown("""
        ### 手順2

        対象物を確認してください。

        **条件を満たすと次の手順へ進みます。**
        """)

    elif st.session_state.step == 3:

        st.markdown("""
        ### 手順3

        次の操作へ進みます。

        🎉 **すべての手順が完了しました！**
        """)


# =========================
# 下部
# =========================

st.divider()

if st.session_state.step >= 3:

    st.success(
        "素晴らしい！すべての手順が完了しました 🎉"
    )

else:

    st.write(
        "カメラを対象物に向けてください。"
    )