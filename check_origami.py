import cv2
import numpy as np
import mediapipe as mp


class OrigamiCV:
    """
    折り紙の状態をCVで判定するクラス。

    return:
        True  -> 正しく折れている
        False -> まだ正しく折れていない
    """

    def __init__(self):

        # カメラ
        self.cap = cv2.VideoCapture(0)

        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def check(self):
        """
        カメラから1フレーム取得して、
        折り紙が正しい状態か判定する。

        Returns
        -------
        bool
            True  : 正しい
            False : 正しくない
        """

        # -----------------------------------------
        # ① カメラから画像を取得
        # -----------------------------------------

        ret, frame = self.cap.read()

        if not ret:
            return False

        # -----------------------------------------
        # ② 青色の検出
        # -----------------------------------------

        hsv = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )

        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([150, 255, 255])

        mask = cv2.inRange(
            hsv,
            lower_blue,
            upper_blue
        )

        # -----------------------------------------
        # ③ ノイズ除去
        # -----------------------------------------

        kernel = np.ones(
            (5, 5),
            np.uint8
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            kernel
        )

        # -----------------------------------------
        # ④ 青い三角形の判定
        # -----------------------------------------

        is_triangle = False

        contours, hierarchy = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if len(contours) > 0:

            largest_contour = max(
                contours,
                key=cv2.contourArea
            )

            area = cv2.contourArea(
                largest_contour
            )

            # 小さすぎる領域は無視
            if area > 1000:

                perimeter = cv2.arcLength(
                    largest_contour,
                    True
                )

                epsilon = 0.02 * perimeter

                approx = cv2.approxPolyDP(
                    largest_contour,
                    epsilon,
                    True
                )

                # 3頂点なら三角形
                if len(approx) == 3:
                    is_triangle = True

        # -----------------------------------------
        # ⑤ MediaPipeで手を検出
        # -----------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:

            hands_visible = True

            # 手の骨格を表示
            for hand_landmarks in results.multi_hand_landmarks:

                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

        else:

            hands_visible = False

        # -----------------------------------------
        # ⑥ 最終判定
        # -----------------------------------------

        if is_triangle and not hands_visible:

            result = True

        else:

            result = False

        # -----------------------------------------
        # ⑦ 画面表示
        # -----------------------------------------

        if result:

            cv2.putText(
                frame,
                "TRUE",
                (50, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (0, 255, 0),
                4
            )

        else:

            cv2.putText(
                frame,
                "FALSE",
                (50, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (0, 0, 255),
                4
            )

        cv2.imshow(
            "Camera",
            frame
        )

        cv2.imshow(
            "Mask",
            mask
        )

        return result

    def close(self):
        """
        カメラとMediaPipeを終了する。
        """

        self.cap.release()
        self.hands.close()
        cv2.destroyAllWindows()


# -----------------------------------------
# 手順管理側から呼び出す関数
# -----------------------------------------

_cv = OrigamiCV()


def check_origami():
    """
    手順管理プログラムから呼び出す関数。

    Returns
    -------
    bool
        True  : 正しく折れている
        False : 正しく折れていない
    """

    return _cv.check()


def close_cv():
    """
    CV処理を終了する。
    """

    _cv.close()

if __name__ == "__main__":

    try:

        while True:

            result = check_origami()

            print("判定結果:", result)

            # qキーで終了
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        close_cv()