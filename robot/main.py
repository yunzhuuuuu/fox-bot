import time
import robot.software.audio_processing.pitch_finder as pf
from robot.software.behaviors import RobotBehaviors
import serial
import time



if __name__ == "__main__":
    port = 'COM3'
    arduino = serial.Serial(port, 9600)
    time.sleep(1)  # wait for Arduino reset after serial connection

    button_pressed = 0
    seen_treat = 0
    is_melody = 0
    # is_melody = pf.run_pitch_finder("output_audio.wav", 8)
    fox = RobotBehaviors(button_pressed, seen_treat, is_melody)

    while True:
        fox.update()
        packet = fox.build_packet()
        arduino.write((packet + "\n").encode()) 
        print("Sent:", packet)
        time.sleep(0.05)  # 20 hz
