import streamlit as st
import av
import cv2

from streamlit_webrtc import (
    webrtc_streamer,
    VideoProcessorBase,
    WebRtcMode,
)


# =========================================================
# Streamlit設定
# =========================================================

st.set_page_config(
    page_title="折り紙チューター：カメラテスト",
    layout="wide",
)


# =========================================================
# タイトル
# =========================================================

st.title("折り紙チューター：カメラ接続テスト")

st.write(
    "下のSTARTボタンを押して、カメラの使用を許可してください。"
)


# =========================================================
# 映像処理クラス
# =========================================================

class OrigamiProcessor(VideoProcessorBase):

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        # WebRTCからフレームを取得
        img = frame.to_ndarray(format="bgr24")

        # 動作確認用の文字を表示
        cv2.putText(
            img,
            "Camera connected",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        # Streamlit-webrtcへフレームを返す
        return av.VideoFrame.from_ndarray(
            img,
            format="bgr24",
        )


# =========================================================
# カメラ表示
# =========================================================

ctx = webrtc_streamer(
    key="origami-cam",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=OrigamiProcessor,
    media_stream_constraints={
        "video": True,
        "audio": False,
    },
)


# =========================================================
# 接続状態の表示
# =========================================================

if ctx.state.playing:
    st.success("カメラが接続されています。")
else:
    st.info("STARTボタンを押してカメラを開始してください。")
