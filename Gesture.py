import mediapipe as mp
import cv2
import numpy as np
import serial
import serial.tools.list_ports
import time

# Function to select a serial port for communication
def select_port():
    ports = list(serial.tools.list_ports.comports())

    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device}")
    
    # Input validation (range check)
    while True: 
        port_index = int(input("Select a port: ")) - 1
        if port_index <= 10 or port_index >= 0:
            break
        print("Invalid port selection, enter again: ")
    return ports[port_index].device

# Function to calculate the angle between two vectors
def get_angle(v1, v2):
    angle = np.dot(v1, v2) / (np.sqrt(np.sum(v1 * v1)) * np.sqrt(np.sum(v2 * v2)))
    angle = np.arccos(angle) / 3.14 * 180
    return angle

# Function to determine the gesture based on finger positions
def get_str_guester(up_fingers, list_lms):
    if len(up_fingers) == 1 and up_fingers[0] == 8:
        v1 = list_lms[6] - list_lms[7]
        v2 = list_lms[8] - list_lms[7]
        angle = get_angle(v1, v2)

        if angle < 160:
            str_guester = "9"
        else:
            str_guester = "1"

    elif len(up_fingers) == 1 and up_fingers[0] == 12:
        str_guester = "Why are you showing that?"

    elif len(up_fingers) == 2 and up_fingers[0] == 8 and up_fingers[1] == 12:
        str_guester = "2"

    elif len(up_fingers) == 2 and up_fingers[0] == 4 and up_fingers[1] == 20:
        str_guester = "6"

    elif len(up_fingers) == 2 and up_fingers[0] == 4 and up_fingers[1] == 8:
        str_guester = "8"

    elif len(up_fingers) == 3 and up_fingers[0] == 8 and up_fingers[1] == 12 and up_fingers[2] == 16:
        str_guester = "3"

    elif len(up_fingers) == 3 and up_fingers[0] == 4 and up_fingers[1] == 8 and up_fingers[2] == 12:
        str_guester = "7"

    elif len(up_fingers) == 4 and up_fingers[0] == 8 and up_fingers[1] == 12 and up_fingers[2] == 16 and up_fingers[3] == 20:
        str_guester = "4"

    elif len(up_fingers) == 5:
        str_guester = "5"

    elif len(up_fingers) == 0:
        str_guester = "10"

    else:
        str_guester = " "

    return str_guester

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    mpHands = mp.solutions.hands

    hands = mpHands.Hands()

    mpDraw = mp.solutions.drawing_utils

    ser = serial.Serial(select_port(), 9600)

    gestureBinds = [0] * 11

    f = open("GestureBinds.txt", "r")

    cnt = 1

    # Read gesture bindings from a file and map them to gestures
    for i in range(6):
        gesture = (int)(f.readline())

        if cnt == 1:
            gestureBinds[gesture] = "x"
        elif cnt == 2:
            gestureBinds[gesture] = "X"
        elif cnt == 3:
            gestureBinds[gesture] = "y"
        elif cnt == 4:
            gestureBinds[gesture] = "Y"
        elif cnt == 5:
            gestureBinds[gesture] = "z"
        elif cnt == 6:
            gestureBinds[gesture] = "Z"

        cnt = cnt + 1

    f.close()

    while True:
        success, img = cap.read()

        if not success:
            continue

        image_height, image_width, _ = np.shape(img)

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]

            mpDraw.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)

            image_height, image_width, _ = np.shape(img)

            list_lms = []

            for i in range(21):
                pos_x = hand.landmark[i].x * image_width
                pos_y = hand.landmark[i].y * image_height
                list_lms.append([int(pos_x), int(pos_y)])

            list_lms = np.array(list_lms, dtype=np.int32)

            hull_index = [0, 1, 2, 3, 6, 10, 14, 19, 18, 17, 10]

            hull = cv2.convexHull(list_lms[hull_index, :])

            cv2.polylines(img, [hull], True, (0, 255, 0), 2)

            ll = [4, 8, 12, 16, 20]

            up_fingers = []

            for i in ll:
                pt = (int(list_lms[i][0]), int(list_lms[i][1]))
                dist = cv2.pointPolygonTest(hull, pt, True)

                if dist < 0:
                    up_fingers.append(i)

            str_guester = get_str_guester(up_fingers, list_lms)

            if str_guester == "1" or str_guester == "2" or str_guester == "3" or str_guester == "4" or str_guester == "5" or str_guester == "6" or str_guester == "7" or str_guester == "8" or str_guester == "9" or str_guester == "10":
                #ser.write(gestureBinds[str_guester])
                print(gestureBinds[int(str_guester)])

            cv2.putText(
                img,
                " %s" % (str_guester),
                (90, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                3,
                (255, 255, 0),
                4,
                cv2.LINE_AA,
            )

            for i in ll:
                pos_x = hand.landmark[i].x * image_width
                pos_y = hand.landmark[i].y * image_height
                cv2.circle(img, (int(pos_x), int(pos_y)), 3, (0, 255, 255), -1)

        cv2.imshow("hands", img)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    cap.release()
