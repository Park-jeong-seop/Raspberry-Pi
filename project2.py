import picamera
import time
import random
import numpy as np
import argparse
import cv2
import RPi.GPIO as GPIO

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
                help = "Path to the image")
args = vars(ap.parse_args())

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

flag = True

led = 4
button = 14
motor = 15

GPIO.setup(led, GPIO.OUT)
GPIO.setup(motor, GPIO.OUT)
GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)

GPIO.output(led, 1)
time.sleep(random.uniform(5, 10))
GPIO.output(led, 0)

while True:
    GPIO.output(led, 1)
    #time.sleep(2)
    #GPIO.output(led, 0)
    
    while flag:
        if GPIO.input(button) == False:
            GPIO.output(led, 0)
            with picamera.PiCamera() as camera:
                camera.start_preview()
                camera.resolution = (250,250)
                time.sleep(2)
                camera.capture('/home/pi/jeong/ExCoin2.png')
                camera.stop_preview()
                time.sleep(2)
            
            image = cv2.imread(args["image"])
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (9,9), 0)
            #cv2.imshow("Image", image)
            #cv2.imshow("Image", blurred)
            #cv2.waitKey(0)

            #edged = cv2.Canny(blurred, 30, 150)
            edged = cv2.Canny(blurred,20, 70)
            #cv2.imshow("Canny", edged)
            #cv2.waitKey(0)

            (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


            coins = image.copy()
            cv2.drawContours(coins, cnts, -1, (0, 255, 0), 2)
            cv2.imshow("Coins", coins)
            cv2.waitKey(0)

            n = 0
            count50 = 0
            count100 = 0
            count500 = 0
            price50 = 0
            price100 = 0
            price500 = 0

            for(i, c) in enumerate(cnts):
                (x, y, w, h) = cv2.boundingRect(c)
                #print("h : ", h)
                #print("w : ", w)
                #print("Coin #{}".format(i+1))
                coin = image[y:y+h, x:x+w]
                
                if(h >= 37 and h <= 41):
                    count50 = count50 + 1
                if(h >= 42 and h <= 46):
                    count100 = count100 + 1
                if(h >= 47 and h <= 52):
                    count500 = count500 +1
                price50 = count50 * 50
                price100 = count100 * 100
                price500 = count500 * 500
                price = price50 + price100 + price500
                
                #cv2.imshow("Coin", coin)

                mask = np.zeros(image.shape[:2], dtype = "uint8")
                ((centerX, centerY), radius) = cv2.minEnclosingCircle(c)
                cv2.circle(mask, (int(centerX), int(centerY)), int(radius), 255, -1)
                mask = mask[y:y+h, x:x+w]
                #cv2.imshow("Masked Coin", cv2.bitwise_and(coin, coin, mask = mask))
                #cv2.waitKey(0)
            print ("50 : ", count50)
            print ("100 : ",count100)
            print ("500 : ",count500)
            print ("price : ", price)
            break
    flag = True



GPIO.cleanup()
