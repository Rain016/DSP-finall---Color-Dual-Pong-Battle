import cv2
import numpy as np
import pygame


# 初始化 Pygame 用於播放音效
pygame.mixer.init()
hit_sound = pygame.mixer.Sound("hit2.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")

# 放寬的HSV紅色範圍
lower_red1 = np.array([0, 100, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 100, 70])
upper_red2 = np.array([180, 255, 255])

# 放寬的HSV黃色範圍
lower_yellow = np.array([15, 100, 100])
upper_yellow = np.array([40, 255, 255])

# 攝影機初始化
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("無法打開攝影機")
    exit()

# 設定攝影機解析度
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# 遊戲參數
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
score_player1 = 0
score_player2 = 0
winning_score = 7  # 勝利分數

# 初始化目標球位置
ball_x = frame_width // 2
ball_y = frame_height // 2
ball_radius = 20
ball_speed_x = 5
ball_speed_y = 5

# 設定球速度的上限
max_ball_speed = 20

# 玩家球拍初始化
player1_x, player1_y = 0, 0
player2_x, player2_y = 0, 0
player1_detected, player2_detected = False, False

# 輸入玩家名稱
player1_name = input("請輸入玩家1的名字: ")
player2_name = input("請輸入玩家2的名字: ")

# 主遊戲邏輯
cv2.namedWindow("Dual Ping Pong", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Dual Ping Pong", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 水平翻轉畫面
    frame = cv2.flip(frame, 1)

    # HSV 色彩空間轉換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 偵測紅色物體（玩家1球拍）
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2

    # 偵測黃色物體（玩家2球拍）
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # 應用模糊處理，減少雜訊
    red_mask = cv2.GaussianBlur(red_mask, (5, 5), 0)
    yellow_mask = cv2.GaussianBlur(yellow_mask, (5, 5), 0)

    # 腐蝕操作（減少雜訊）
    red_mask = cv2.erode(red_mask, None, iterations=2)
    yellow_mask = cv2.erode(yellow_mask, None, iterations=2)

    # 膨脹操作（增強偵測到的區域）
    red_mask = cv2.dilate(red_mask, None, iterations=2)
    yellow_mask = cv2.dilate(yellow_mask, None, iterations=2)

    # 找到玩家1球拍的位置
    contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours_red:
        largest_contour_red = max(contours_red, key=cv2.contourArea)
        M_red = cv2.moments(largest_contour_red)
        if M_red["m00"] > 0:
            player1_x = int(M_red["m10"] / M_red["m00"])
            player1_y = int(M_red["m01"] / M_red["m00"])
            player1_detected = True

    # 找到玩家2球拍的位置
    contours_yellow, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours_yellow:
        largest_contour_yellow = max(contours_yellow, key=cv2.contourArea)
        M_yellow = cv2.moments(largest_contour_yellow)
        if M_yellow["m00"] > 0:
            player2_x = int(M_yellow["m10"] / M_yellow["m00"])
            player2_y = int(M_yellow["m01"] / M_yellow["m00"])
            player2_detected = True

    # 動態移動目標球
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # 確保球在畫面內
    if ball_y <= ball_radius or ball_y >= frame_height - ball_radius:
        ball_speed_y = -ball_speed_y

    # 球到左邊界
    if ball_x <= ball_radius:
        # 檢查是否進入玩家2的球門範圍
        if frame_height // 3 <= ball_y <= frame_height * 2 // 3:
            score_player2 += 1
            pygame.mixer.Sound.play(hit_sound)
            ball_x, ball_y = frame_width // 2, frame_height // 2
            ball_speed_x = 5
            ball_speed_y = 5
        else:
            ball_speed_x = -ball_speed_x

    # 球到右邊界
    if ball_x >= frame_width - ball_radius:
        # 檢查是否進入玩家1的球門範圍
        if frame_height // 3 <= ball_y <= frame_height * 2 // 3:
            score_player1 += 1
            pygame.mixer.Sound.play(hit_sound)
            ball_x, ball_y = frame_width // 2, frame_height // 2
            ball_speed_x = 5
            ball_speed_y = 5
        else:
            ball_speed_x = -ball_speed_x

    # 玩家1與球的碰撞檢測
    if player1_detected:
        distance1 = np.sqrt((ball_x - player1_x) ** 2 + (ball_y - player1_y) ** 2)
        if distance1 < ball_radius + 20:
            pygame.mixer.Sound.play(hit_sound)
            dx = ball_x - player1_x
            dy = ball_y - player1_y
            magnitude = np.sqrt(dx**2 + dy**2)
            ball_speed_x = (dx / magnitude) * max_ball_speed
            ball_speed_y = (dy / magnitude) * max_ball_speed

    # 玩家2與球的碰撞檢測
    if player2_detected:
        distance2 = np.sqrt((ball_x - player2_x) ** 2 + (ball_y - player2_y) ** 2)
        if distance2 < ball_radius + 20:
            pygame.mixer.Sound.play(hit_sound)
            dx = ball_x - player2_x
            dy = ball_y - player2_y
            magnitude = np.sqrt(dx**2 + dy**2)
            ball_speed_x = (dx / magnitude) * max_ball_speed
            ball_speed_y = (dy / magnitude) * max_ball_speed

    # 畫球、球拍及球門範圍
    cv2.circle(frame, (int(ball_x), int(ball_y)), ball_radius, (0, 0, 255), -1)  # 主球
    if player1_detected:
        cv2.circle(frame, (int(player1_x), int(player1_y)), 20, (255, 0, 0), 2)  # 玩家1球拍
    if player2_detected:
        cv2.circle(frame, (int(player2_x), int(player2_y)), 20, (0, 255, 255), 2)  # 玩家2球拍
    cv2.rectangle(frame, (0, frame_height // 3), (30, frame_height * 2 // 3), (0, 255, 0), 2)  # 玩家2球門
    cv2.rectangle(frame, (frame_width - 30, frame_height // 3), (frame_width, frame_height * 2 // 3), (0, 255, 0), 2)  # 玩家1球門

    # 顯示分數
    cv2.putText(frame, f"{player1_name} Score: {score_player1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"{player2_name} Score: {score_player2}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 檢查是否有玩家達到勝利分數
    if score_player1 >= winning_score:
        cv2.putText(frame, f"{player1_name} Wins!", (frame_width // 4, frame_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        pygame.mixer.Sound.play(game_over_sound)
        cv2.imshow("Dual Ping Pong", frame)
        cv2.waitKey(2000)  # 等待2秒鐘，顯示結束畫面
        break
    elif score_player2 >= winning_score:
        cv2.putText(frame, f"{player2_name} Wins!", (frame_width // 4, frame_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        pygame.mixer.Sound.play(game_over_sound)
        cv2.imshow("Dual Ping Pong", frame)
        cv2.waitKey(2000)  # 等待2秒鐘，顯示結束畫面
        break

    # 顯示畫面
    cv2.imshow("Dual Ping Pong", frame)

    # 提前退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
print(f"遊戲結束！{player1_name} 分數：{score_player1}，{player2_name} 分數：{score_player2}")