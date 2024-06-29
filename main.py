# https://google.github.io/mediapipe/solutions/pose.html
# https://colab.research.google.com/drive/1uCuA6We9T5r0WljspEHWPHXCT_2bMKUy#scrollTo=BAivyQ_xOtFp

# https://google.github.io/mediapipe/getting_started/python.html
# https://developers.google.com/mediapipe/framework/getting_started/install#installing_on_windows

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# every image or video will be scaled to match this height in pixels
const_image_height = 650
# Frames to skip for Reba score graph update
skip = 1
times = 0


#  calculate angle
def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # mid
    c = np.array(c)  # End
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    _angle = np.abs(radians * 180.0 / np.pi)
    if _angle > 180:
        _angle = 360 - _angle
    return int(_angle)


# calculate angle (for 3d coordinates)
# def calculate_angle(first_pt, mid_pt, end_pt):
#     a = np.array(first_pt)
#     b = np.array(mid_pt)
#     c = np.array(end_pt)
#     ba = a - b
#     bc = c - b
#     cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
#     angle = np.arccos(cosine_angle)
#     _angle = np.degrees(angle)
#     return _angle


cap = cv2.VideoCapture(0)  # just for initialisation
cap.release()
g_success, g_image = cap.read()


def menu_select_camera():
    global cap
    cap.release()
    cap = cv2.VideoCapture(0)
    global photo_mode
    photo_mode = 1


def menu_select_video():
    temp_file = filedialog.askopenfile(parent=window, title='Select a photo or video file only')
    if temp_file.name:
        global cap
        cap.release()
        cap = cv2.VideoCapture(temp_file.name)
        global photo_mode
        photo_mode = 1


def menu_show_help():
    global cap
    cap.release()
    global photo_mode
    photo_mode = 0


# Set up GUI
window = tk.Tk()  # Makes main window
window.resizable(False, False)
window.wm_title("Posture Analyser")
# window.config(background="#FFFFFF")

menu = tk.Menu(window)
fileMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label='File', menu=fileMenu)
fileMenu.add_command(label='Camera', command=menu_select_camera)
fileMenu.add_command(label='Open...', command=menu_select_video)
fileMenu.add_separator()
fileMenu.add_command(label='Exit', command=window.destroy)
settingMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label='Settings', menu=settingMenu)
settingMenu.add_command(label='variables')
helpMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label='Help', menu=helpMenu)
helpMenu.add_command(label='About', command=menu_show_help)
window.config(menu=menu)

photo_mode = 0
imageFrame = tk.Frame(window, highlightbackground="black", highlightthickness=1)
lmain = tk.Label(imageFrame)
lmain.pack()
imageFrame.grid(row=0, column=0, padx=10, pady=10)

uiFrameMain = tk.Frame(window)
uiFrameMain.grid(row=0, column=1)
uiFrameREBA = tk.Frame(uiFrameMain)
uiFrameREBA.grid(row=0, column=0)
uiFrameScores = ttk.Notebook(uiFrameMain, padding=10)
uiFrameScores.grid(row=1, column=0)

####################

uiFrame1 = tk.LabelFrame(uiFrameREBA, text='REBA SCORE')
uiFrame1.grid(row=0, column=0, padx=10, pady=10)
uiLabel_mainRebaScore = tk.Label(uiFrame1, text='0', font=("Arial", 20), width=2)
uiLabel_mainRebaScore.grid(row=0, column=0)
uiLabel_mainRebaScoreStatus = tk.Label(uiFrame1, text='-', wraplength=200)
uiLabel_mainRebaScoreStatus.grid(row=0, column=1)

_graphSize = 200
_graphDivNum = 14
_graphDiv = _graphSize / _graphDivNum
_pointsNum = 17
_pitch = _graphSize / _pointsNum
_pointsIndex = 0
_pointsBuffer = [0] * _pointsNum
uiGraph = tk.Canvas(uiFrame1, width=_graphSize, height=_graphSize, bg='#000')
for i in range(1, 14):
    uiGraph.create_text(6, i * _graphDiv, text=13-i, fill="#fff")
uiGraph.grid(row=1, column=1)

uiLabel_graph_x = tk.Label(uiFrame1, text='REBA', wraplength=1)
uiLabel_graph_x.grid(row=1, column=0)
uiLabel_graph_x = tk.Label(uiFrame1, text='Time (per Frame)')
uiLabel_graph_x.grid(row=2, column=1)
uiFlag_drawLandmarks = tk.IntVar()
uiCheck_neckTwist = tk.Checkbutton(uiFrame1, text="Draw Body Frame Landmarks", variable=uiFlag_drawLandmarks, onvalue=1,
                                   offvalue=0)
uiCheck_neckTwist.grid(row=3, column=1)


def update_graph(score):
    # score = 12
    uiGraph.create_rectangle(_pitch, 8, _graphSize, _graphSize-_pitch, fill='#000')
    for i in range(1, _graphDivNum):  # grid
        uiGraph.create_line(_pitch, i * _graphDiv, _graphSize, i * _graphDiv, fill="#777", width=1)
        uiGraph.create_line(i*_graphDiv, 0, i*_graphDiv, _graphSize, fill="#777", width=1)
    global _pointsIndex
    _pointsBuffer[_pointsIndex] = score
    _pointsIndex += 1
    if _pointsIndex >= _pointsNum:
        _pointsIndex = 0

    # for i in range(0, _pointsNum):  # bar graph
    #     index = _pointsIndex - i
    #     if index < 0:
    #         index += _pointsNum
    #     val = _pointsBuffer[index]
    #     if val < 3:
    #         col = '#0f0'
    #     elif val < 9:
    #         col = '#ff0'
    #     else:
    #         col = '#f00'
    #     uiGraph.create_line(_graphSize - i * _pitch, _graphSize - _graphDiv, _graphSize - i * _pitch, _graphSize - (val+1)*_graphDiv, fill=col, width=_pitch)

    for i in range(1, _pointsNum):  # line graph
        index = _pointsIndex - i
        if index < 0:
            index += _pointsNum
        pval = _pointsBuffer[index - 1]
        val = _pointsBuffer[index]
        if val < 3:
            col = '#0f0'
        elif val < 9:
            col = '#ff0'
        else:
            col = '#f00'
        uiGraph.create_line(_graphSize - i * _pitch,
                            _graphSize - (pval + 1) * _graphDiv,
                            _graphSize - (i - 1) * _pitch,
                            _graphSize - (val + 1) * _graphDiv,
                            fill=col, width=2)


####################

uiFrame2 = ttk.Frame(uiFrameScores)  # SCORE A
uiFrame2.grid(row=1, column=0, padx=10, pady=10)

uiLabel_neckAngle_info = tk.Label(uiFrame2, text='Neck angle')
uiLabel_neckAngle_info.configure(width=13)
uiLabel_neckAngle_info.grid(row=0, column=0)
uiLabel_neckAngle = tk.Label(uiFrame2, text='-', width=4)
uiLabel_neckAngle.grid(row=0, column=1)
uiLabel_neckScore_info = tk.Label(uiFrame2, text='Neck score')
uiLabel_neckScore_info.grid(row=1, column=0)
uiLabel_neckScore = tk.Label(uiFrame2, text='-', width=4)
uiLabel_neckScore.grid(row=1, column=1)
uiFlag_neckTwist = tk.IntVar()
uiFlag_neckBent = tk.IntVar()
uiCheck_neckTwist = tk.Checkbutton(uiFrame2, text="Twisted", variable=uiFlag_neckTwist, onvalue=1,
                                   offvalue=0)
uiCheck_neckTwist.grid(row=2, column=0)
uiCheck_neckBent = tk.Checkbutton(uiFrame2, text="Bent", variable=uiFlag_neckBent, onvalue=1, offvalue=0)
uiCheck_neckBent.grid(row=2, column=1)

uiLabel_trunkAngle_info = tk.Label(uiFrame2, text='Trunk angle')
uiLabel_trunkAngle_info.grid(row=3, column=0)
uiLabel_trunkAngle = tk.Label(uiFrame2, text='-', width=4)
uiLabel_trunkAngle.grid(row=3, column=1)
uiLabel_trunkScore_info = tk.Label(uiFrame2, text='Trunk score')
uiLabel_trunkScore_info.grid(row=4, column=0)
uiLabel_trunkScore = tk.Label(uiFrame2, text='-', width=4)
uiLabel_trunkScore.grid(row=4, column=1)
uiFlag_trunkTwist = tk.IntVar()
uiCheck_trunkTwist = tk.Checkbutton(uiFrame2, text="Twisted", variable=uiFlag_trunkTwist, onvalue=1,
                                    offvalue=0)
uiCheck_trunkTwist.grid(row=5, column=0)
uiFlag_trunkBent = tk.IntVar()
uiCheck_trunkBent = tk.Checkbutton(uiFrame2, text="Bent", variable=uiFlag_trunkBent, onvalue=1, offvalue=0)
uiCheck_trunkBent.grid(row=5, column=1)

uiLabel_legPosition_info = tk.Label(uiFrame2, text='Legs angle')
uiLabel_legPosition_info.grid(row=6, column=0)
uiStr_legPosition = tk.StringVar()
uiStr_legPosition.set("0-30")
uiMenu_legPosition = tk.OptionMenu(uiFrame2, uiStr_legPosition, "0-30", "30-60", "60+")
uiMenu_legPosition.configure(width=10)
uiMenu_legPosition.grid(row=6, column=1)
uiFlag_legRaised = tk.IntVar()
uiCheck_legRaised = tk.Checkbutton(uiFrame2, text="Leg raised", variable=uiFlag_legRaised, onvalue=1, offvalue=0)
uiCheck_legRaised.grid(row=7, column=0)
uiLabel_legScore_info = tk.Label(uiFrame2, text='Legs score')
uiLabel_legScore_info.grid(row=8, column=0)
uiLabel_legScore = tk.Label(uiFrame2, text='-', width=4)
uiLabel_legScore.grid(row=8, column=1)

uiLabel_load_info = tk.Label(uiFrame2, text='Load adjust')
uiLabel_load_info.grid(row=9, column=0)
uiStr_load = tk.StringVar()
uiStr_load.set("< 11 lbs")
uiMenu_load = tk.OptionMenu(uiFrame2, uiStr_load, "< 11 lbs", "11-22 lbs", "> 22 lbs")
uiMenu_load.configure(width=10)
uiMenu_load.grid(row=9, column=1)
uiFlag_loadRapid = tk.IntVar()
uiCheck_loadRapid = tk.Checkbutton(uiFrame2, text="Rapid", variable=uiFlag_loadRapid, onvalue=1,
                                   offvalue=0)
uiCheck_loadRapid.grid(row=10, column=0)
uiLabel_loadScore_info = tk.Label(uiFrame2, text='Load score')
uiLabel_loadScore_info.grid(row=11, column=0)
uiLabel_loadScore = tk.Label(uiFrame2, text='-', width=4)
uiLabel_loadScore.grid(row=11, column=1)

####################

uiFrame3 = ttk.Frame(uiFrameScores)  # SCORE B
uiFrame3.grid(row=2, column=0, padx=10, pady=10)

uiLabel_bodySide_info = tk.Label(uiFrame3, text='Body Side')
uiLabel_bodySide_info.configure(width=13)
uiLabel_bodySide_info.grid(row=0, column=0)
uiStr_bodySide = tk.StringVar()
uiStr_bodySide.set("Left")
uiMenu_bodySide = tk.OptionMenu(uiFrame3, uiStr_bodySide, "Left", "Right")
uiMenu_bodySide.configure(width=10)
uiMenu_bodySide.grid(row=0, column=1)

uiLabel_upperArmAngle_info = tk.Label(uiFrame3, text='UpperArm angle')
uiLabel_upperArmAngle_info.grid(row=1, column=0)
uiLabel_upperArmAngle = tk.Label(uiFrame3, text='-', width=4)
uiLabel_upperArmAngle.grid(row=1, column=1)
uiLabel_upperArmScore_info = tk.Label(uiFrame3, text='UpperArm score')
uiLabel_upperArmScore_info.grid(row=2, column=0)
uiLabel_upperArmScore = tk.Label(uiFrame3, text='-', width=4)
uiLabel_upperArmScore.grid(row=2, column=1)
uiFlag_armRaised = tk.IntVar()
uiFlag_armAbducted = tk.IntVar()
uiFlag_armSupport = tk.IntVar()
uiCheck_armRaised = tk.Checkbutton(uiFrame3, text="Raised", variable=uiFlag_armRaised, onvalue=1,
                                   offvalue=0)
uiCheck_armRaised.grid(row=3, column=0)
uiCheck_armAbducted = tk.Checkbutton(uiFrame3, text="Abducted", variable=uiFlag_armAbducted, onvalue=1,
                                     offvalue=0)
uiCheck_armAbducted.grid(row=3, column=1)
uiCheck_armAbducted = tk.Checkbutton(uiFrame3, text="Support", variable=uiFlag_armSupport, onvalue=1,
                                     offvalue=0)
uiCheck_armAbducted.grid(row=4, column=0)

uiLabel_lowerArmAngle_info = tk.Label(uiFrame3, text='lowerArm angle')
uiLabel_lowerArmAngle_info.grid(row=5, column=0)
uiLabel_lowerArmAngle = tk.Label(uiFrame3, text='-', width=4)
uiLabel_lowerArmAngle.grid(row=5, column=1)
uiLabel_lowerArmScore_info = tk.Label(uiFrame3, text='lowerArm score')
uiLabel_lowerArmScore_info.grid(row=6, column=0)
uiLabel_lowerArmScore = tk.Label(uiFrame3, text='-', width=4)
uiLabel_lowerArmScore.grid(row=6, column=1)

uiLabel_wrist_info = tk.Label(uiFrame3, text='Wrist position')
uiLabel_wrist_info.grid(row=7, column=0)
uiStr_wrist = tk.StringVar()
uiStr_wrist.set("15 center")
uiMenu_wrist = tk.OptionMenu(uiFrame3, uiStr_wrist, "15+ up", "15 center", "15+ down")
uiMenu_wrist.configure(width=10)
uiMenu_wrist.grid(row=7, column=1)
uiFlag_wristBent = tk.IntVar()
uiCheck_wristBent = tk.Checkbutton(uiFrame3, text="Bent/Twist", variable=uiFlag_wristBent, onvalue=1,
                                   offvalue=0)
uiCheck_wristBent.grid(row=8, column=0)
uiLabel_wristScore_info = tk.Label(uiFrame3, text='Wrist score')
uiLabel_wristScore_info.grid(row=9, column=0)
uiLabel_wristScore = tk.Label(uiFrame3, text='-', width=4)
uiLabel_wristScore.grid(row=9, column=1)

uiLabel_coupling_info = tk.Label(uiFrame3, text='Coupling')
uiLabel_coupling_info.grid(row=10, column=0)
uiStr_coupling = tk.StringVar()
uiStr_coupling.set("fair")
uiMenu_coupling = tk.OptionMenu(uiFrame3, uiStr_coupling, "good", "fair", "poor", "unaccepted")
uiMenu_coupling.configure(width=10)
uiMenu_coupling.grid(row=10, column=1)
uiLabel_couplingScore_info = tk.Label(uiFrame3, text='Coupling score')
uiLabel_couplingScore_info.grid(row=11, column=0)
uiLabel_couplingScore = tk.Label(uiFrame3, text='-', width=4)
uiLabel_couplingScore.grid(row=11, column=1)

####################

uiFrame4 = ttk.Frame(uiFrameScores)  # REBA
uiFrame4.grid(row=2, column=0, padx=10, pady=10)

uiLabel_score_a_info = tk.Label(uiFrame4, text='Score A')
uiLabel_score_a_info.grid(row=0, column=0)
uiLabel_score_a = tk.Label(uiFrame4, text='-', width=4)
uiLabel_score_a.grid(row=0, column=1)

uiLabel_score_b_info = tk.Label(uiFrame4, text='Score B')
uiLabel_score_b_info.grid(row=1, column=0)
uiLabel_score_b = tk.Label(uiFrame4, text='-', width=4)
uiLabel_score_b.grid(row=1, column=1)

uiLabel_score_c_info = tk.Label(uiFrame4, text='Score C')
uiLabel_score_c_info.grid(row=2, column=0)
uiLabel_score_c = tk.Label(uiFrame4, text='-', width=4)
uiLabel_score_c.grid(row=2, column=1)

uiLabel_score_activity_info = tk.Label(uiFrame4, text='Activity Score:')
uiLabel_score_activity_info.grid(row=3, column=0)
uiFlag_activity1 = tk.IntVar()
uiFlag_activity2 = tk.IntVar()
uiFlag_activity3 = tk.IntVar()
uiCheck_activity1 = tk.Checkbutton(uiFrame4, text="Hold >1 min", variable=uiFlag_activity1, onvalue=1,
                                   offvalue=0)
uiCheck_activity2 = tk.Checkbutton(uiFrame4, text="Repeat >4X/min", variable=uiFlag_activity2, onvalue=1,
                                   offvalue=0)
uiCheck_activity3 = tk.Checkbutton(uiFrame4, text="Rapid changes", variable=uiFlag_activity3, onvalue=1,
                                   offvalue=0)
uiCheck_activity1.grid(row=4, column=0)
uiCheck_activity2.grid(row=5, column=0)
uiCheck_activity3.grid(row=6, column=0)

uiLabel_score_reba_info = tk.Label(uiFrame4, text='REBA')
uiLabel_score_reba_info.grid(row=7, column=0)
uiLabel_score_reba = tk.Label(uiFrame4, text='-', width=4)
uiLabel_score_reba.grid(row=7, column=1)

recording = 0
data = ["hello"]


def save_data_file():
    global recording, data

    if recording == 0:
        recording = 1
        uiButton_save.configure(text="STOP")
        uiLabel_save.configure(text="Recording data")
        uiLabel_save.configure(bg="red", fg="white")
        data = []
    else:
        recording = 0
        uiButton_save.configure(text="START")
        uiLabel_save.configure(text="Not recording")
        uiLabel_save.configure(bg="yellow", fg="black")
        file1 = open("Data record.csv", "w")
        file1.writelines(data)
        file1.close()


uiLabel_save = tk.Label(uiFrame4, text='Not recording')
uiLabel_save.configure(bg="yellow", fg="black")
uiLabel_save.grid(row=8, column=0)
uiButton_save = tk.Button(uiFrame4, text='START', command=save_data_file)
uiButton_save.grid(row=8, column=1)

####################

uiFrameScores.add(uiFrame2, text='SCORE A ')
uiFrameScores.add(uiFrame3, text='SCORE B ')
uiFrameScores.add(uiFrame4, text=' REBA ')

####################
angle_neck = 0
angle_trunk = 0
angle_upper_arm = 0
angle_lower_arm = 0
score_neck = 0
score_trunk = 0
score_leg = 0
score_load = 0
score_upper_arm = 0
score_lower_arm = 0
score_wrist = 0
score_coupling = 0
score_activity = 0
score_post_A = 0
score_final_A = 0
score_post_B = 0
score_final_B = 0
score_final_C = 0
score_reba = 0


def calculate_scores():
    global angle_neck, angle_trunk, angle_upper_arm, angle_lower_arm
    global score_neck, score_trunk, score_leg, score_load, score_upper_arm, score_lower_arm, score_wrist, score_coupling, score_activity
    global score_post_A, score_final_A, score_post_B, score_final_B, score_final_C, score_reba

    # NECK SCORE
    if angle_neck < 20:
        score_neck = 1
    elif angle_neck >= 20:
        score_neck = 2
    if uiFlag_neckBent.get() == 1:
        score_neck += 1
    elif uiFlag_neckTwist.get() == 1:
        score_neck += 1

    # TRUNK SCORE
    if angle_trunk == 0:
        score_trunk = 1
    elif angle_trunk < 20:
        score_trunk = 2
    elif angle_trunk < 60:
        score_trunk = 3
    elif angle_trunk >= 60:
        score_trunk = 4
    if uiFlag_trunkBent.get() == 1:
        score_trunk += 1
    elif uiFlag_trunkTwist.get() == 1:
        score_trunk += 1

    # LEG SCORE
    score_leg = 1
    if uiFlag_legRaised.get() == 1:
        score_leg += 1
    if uiStr_legPosition.get() == "30-60":
        score_leg += 1
    elif uiStr_legPosition.get() == "60+":
        score_leg += 2

    # LOAD SCORE
    if uiStr_load.get() == "< 11 lbs":
        score_load = 0
    elif uiStr_load.get() == "11-22 lbs":
        score_load = 1
    elif uiStr_load.get() == "> 22 lbs":
        score_load = 2
    if uiFlag_loadRapid.get() == 1:
        score_load += 1

    # UPPER ARM SCORE
    if angle_upper_arm < 20:
        score_upper_arm = 1
    elif angle_upper_arm < 45:
        score_upper_arm = 2
    elif angle_upper_arm < 90:
        score_upper_arm = 3
    elif angle_upper_arm >= 90:
        score_upper_arm = 4
    if uiFlag_armRaised.get() == 1:
        score_upper_arm += 1
    if uiFlag_armAbducted.get() == 1:
        score_upper_arm += 1
    if uiFlag_armSupport.get() == 1 and score_upper_arm >= 2:
        score_upper_arm -= 1

    # LOWER ARM SCORE
    if angle_lower_arm < 60:
        score_lower_arm = 2
    elif angle_lower_arm < 100:
        score_lower_arm = 1
    elif angle_lower_arm >= 100:
        score_lower_arm = 2

    # WRIST SCORE
    if uiStr_wrist.get() == "15+ up":
        score_wrist = 2
    elif uiStr_wrist.get() == "15 center":
        score_wrist = 1
    elif uiStr_wrist.get() == "15+ down":
        score_wrist = 2
    if uiFlag_wristBent.get() == 1:
        score_wrist += 1

    # COUPLING SCORE
    if uiStr_coupling.get() == "good":
        score_coupling = 0
    elif uiStr_coupling.get() == "fair":
        score_coupling = 1
    elif uiStr_coupling.get() == "poor":
        score_coupling = 2
    elif uiStr_coupling.get() == "unaccepted":
        score_coupling = 3

    # ACTIVITY SCORE
    score_activity = 0
    if uiFlag_activity1.get() == 1:
        score_activity += 1
    if uiFlag_activity2.get() == 1:
        score_activity += 1
    if uiFlag_activity3.get() == 1:
        score_activity += 1

    # SCORE A TABLE
    score_post_A = 0
    if score_neck == 1:
        if score_leg == 1:
            if score_trunk <= 2:
                score_post_A = score_trunk
            elif score_trunk == 3:
                score_post_A = 2
            else:
                score_post_A = score_trunk - 1
        elif score_leg == 2:
            score_post_A = score_trunk + 1
        elif score_leg == 3:
            score_post_A = score_trunk + 2
        elif score_leg == 4:
            score_post_A = score_trunk + 3
    elif score_neck == 2:
        if score_trunk == 1:
            score_post_A = score_leg
        elif score_leg == 1:
            score_post_A = score_trunk + 1
        elif score_leg == 2:
            score_post_A = score_trunk + 2
        elif score_leg == 3:
            score_post_A = score_trunk + 3
        elif score_leg == 4:
            score_post_A = score_trunk + 4
    elif score_neck == 3:
        if score_leg == 1:
            score_post_A = score_trunk + 2
        elif score_leg == 2:
            if score_trunk == 1:
                score_post_A = 3
            else:
                score_post_A = score_trunk + 3
        elif score_leg == 3:
            score_post_A = score_trunk + 4
        elif score_leg == 4:
            if score_trunk == 5:
                score_post_A = 9
            else:
                score_post_A = score_trunk + 5

    # SCORE B TABLE
    if score_wrist == 3:
        if score_lower_arm == 1:
            if score_upper_arm == 1:
                score_post_B = 2
            elif score_upper_arm == 4:
                score_post_B = 5
            elif score_upper_arm == 6:
                score_post_B = 8
        elif score_lower_arm == 2:
            if score_upper_arm == 3:
                score_post_B = 5
            elif score_upper_arm == 5:
                score_post_B = 8
            elif score_upper_arm == 6:
                score_post_B = 9
    else:
        if score_upper_arm == 1:
            score_post_B = score_wrist
        elif score_upper_arm == 2:
            score_post_B = score_wrist + score_lower_arm - 1
        elif score_upper_arm == 3:
            score_post_B = score_wrist + score_lower_arm + 1
        elif score_upper_arm == 4:
            score_post_B = score_wrist + score_lower_arm + 2
        elif score_upper_arm == 5:
            score_post_B = score_wrist + score_lower_arm + 4
        elif score_upper_arm == 6:
            score_post_B = score_wrist + score_lower_arm + 5

    # SCORE C TABLE
    if score_final_A == 1:
        if score_final_B <= 3:
            score_final_C = 1
        elif score_final_B <= 5:
            score_final_C = score_final_B - 2
        elif score_final_B <= 9:
            score_final_C = score_final_B - 3
        else:
            score_final_C = 7
    elif score_final_A == 2:
        if score_final_B <= 2:
            score_final_C = score_final_B
        elif score_final_B <= 5:
            score_final_C = score_final_B - 1
        elif score_final_B <= 8:
            score_final_C = score_final_B - 2
        elif score_final_B <= 10:
            score_final_C = score_final_B - 3
        else:
            score_final_C = score_final_B - 4
    elif score_final_A == 3:
        if score_final_B <= 1:
            score_final_C = 2
        elif score_final_B <= 4:
            score_final_C = 3
        elif score_final_B <= 7:
            score_final_C = score_final_B - 1
        elif score_final_B <= 9:
            score_final_C = 7
        else:
            score_final_C = 8
    elif score_final_A == 4:
        if score_final_B <= 1:
            score_final_C = 3
        elif score_final_B <= 4:
            score_final_C = 4
        elif score_final_B <= 7:
            score_final_C = score_final_B
        elif score_final_B <= 9:
            score_final_C = 8
        else:
            score_final_C = 9
    elif score_final_A == 5:
        if score_final_B <= 3:
            score_final_C = 4
        elif score_final_B <= 7:
            score_final_C = score_final_B + 1
        elif score_final_B <= 8:
            score_final_C = 8
        else:
            score_final_C = 9
    elif score_final_A == 6:
        if score_final_B <= 3:
            score_final_C = 6
        elif score_final_B <= 4:
            score_final_C = 7
        elif score_final_B <= 6:
            score_final_C = 8
        elif score_final_B <= 8:
            score_final_C = 9
        else:
            score_final_C = 10
    elif score_final_A == 7:
        if score_final_B <= 3:
            score_final_C = 7
        elif score_final_B <= 4:
            score_final_C = 8
        elif score_final_B <= 7:
            score_final_C = 9
        elif score_final_B <= 9:
            score_final_C = 10
        else:
            score_final_C = 11
    elif score_final_A == 8:
        if score_final_B <= 3:
            score_final_C = 8
        elif score_final_B <= 4:
            score_final_C = 9
        elif score_final_B <= 9:
            score_final_C = 10
        else:
            score_final_C = 10
    elif score_final_A == 9:
        if score_final_B <= 3:
            score_final_C = 9
        elif score_final_B <= 6:
            score_final_C = 10
        elif score_final_B <= 9:
            score_final_C = 11
        else:
            score_final_C = 12
    elif score_final_A == 10:
        if score_final_B <= 3:
            score_final_C = 10
        elif score_final_B <= 7:
            score_final_C = 11
        else:
            score_final_C = 12
    elif score_final_A == 11:
        if score_final_B <= 4:
            score_final_C = 11
        else:
            score_final_C = 12
    else:
        score_final_C = 12

    score_final_A = score_post_A + score_load
    score_final_B = score_post_B + score_coupling
    score_reba = score_final_C + score_activity

    uiLabel_neckScore.configure(text=score_neck)
    uiLabel_trunkScore.configure(text=score_trunk)
    uiLabel_legScore.configure(text=score_leg)
    uiLabel_loadScore.configure(text=score_load)
    uiLabel_upperArmScore.configure(text=score_upper_arm)
    uiLabel_lowerArmScore.configure(text=score_lower_arm)
    uiLabel_wristScore.configure(text=score_wrist)
    uiLabel_couplingScore.configure(text=score_coupling)
    uiLabel_score_a.configure(text=score_final_A)
    uiLabel_score_b.configure(text=score_final_B)
    uiLabel_score_c.configure(text=score_final_C)
    uiLabel_score_reba.configure(text=score_reba)
    uiLabel_mainRebaScore.configure(text=score_reba)

    if score_reba < 2:
        uiLabel_mainRebaScoreStatus.configure(text="Negligible risk")
    elif score_reba < 4:
        uiLabel_mainRebaScoreStatus.configure(text="Low risk. Change may be needed")
    elif score_reba < 8:
        uiLabel_mainRebaScoreStatus.configure(text="Medium risk. Further investigate. Change soon")
    elif score_reba < 11:
        uiLabel_mainRebaScoreStatus.configure(text="High risk. Investigate and implement change")
    else:
        uiLabel_mainRebaScoreStatus.configure(text="Very high risk. Implement change")


####################


# detection model settings
pose = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=1,
    enable_segmentation=True,
    min_detection_confidence=0.1)


def show_frame():
    if photo_mode == 0:
        image = Image.open("welcome screen.png")
        actual_height = const_image_height
        actual_width = int(image.width * const_image_height / image.height)
        image = image.resize((actual_width, actual_height))
        imgtk = ImageTk.PhotoImage(image)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)

    elif photo_mode == 1:
        success, image = cap.read()
        global g_image, times, angle_neck, angle_trunk, angle_upper_arm, angle_lower_arm
        if success:
            g_image = image
        else:
            image = g_image
        image_height = image.shape[0]
        image_width = image.shape[1]
        # print(image_width, image_height)
        actual_height = const_image_height
        actual_width = int(image_width * const_image_height / image_height)
        image = cv2.resize(image, (actual_width, actual_height))
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        # Draw the pose annotation on the image.
        image.flags.writeable = True
        # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        try:
            landmarks = results.pose_landmarks.landmark
            pt_head = [(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x +
                        landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x) * actual_width / 2.0,
                       (landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y +
                        landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].y) * actual_height / 2.0]
            pt_shoulder_mid = [(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x +
                                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x) * actual_width / 2.0,
                               (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y +
                                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) * actual_height / 2.0]
            pt_hip_mid = [(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x +
                           landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x) * actual_width / 2.0,
                          (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y +
                           landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y) * actual_height / 2.0]
            pt_shoulder = 0
            pt_elbow = 0
            pt_wrist = 0

            if uiStr_bodySide.get() == "Left":
                pt_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * actual_width,
                               landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * actual_height]
                pt_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * actual_width,
                            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * actual_height]
                pt_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * actual_width,
                            landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * actual_height]
            else:
                pt_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * actual_width,
                               landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * actual_height]
                pt_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * actual_width,
                            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * actual_height]
                pt_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * actual_width,
                            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * actual_height]

            angle_neck = calculate_angle(pt_head, pt_shoulder_mid, [pt_shoulder_mid[0], pt_shoulder_mid[1] - 10])
            uiLabel_neckAngle.configure(text=str(angle_neck) + '°')
            angle_trunk = calculate_angle(pt_shoulder_mid, pt_hip_mid, [pt_hip_mid[0], pt_hip_mid[1] - 10])
            uiLabel_trunkAngle.configure(text=str(angle_trunk) + '°')
            angle_upper_arm = calculate_angle(pt_elbow, pt_shoulder, [pt_shoulder[0], pt_shoulder[1] + 10])
            uiLabel_upperArmAngle.configure(text=str(angle_upper_arm) + '°')
            angle_lower_arm = calculate_angle(pt_wrist, pt_elbow, [pt_elbow[0], pt_elbow[1] + 10])
            uiLabel_lowerArmAngle.configure(text=str(angle_lower_arm) + '°')

            calculate_scores()
            data.append(str(score_reba) + '\n')

            times += 1
            if times > skip:
                times = 0
                update_graph(score_reba)

        except:
            pass
        if uiFlag_drawLandmarks.get():
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        img = Image.fromarray(image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)

    lmain.after(20, show_frame)


show_frame()  # Display 2
window.mainloop()  # Starts GUI
