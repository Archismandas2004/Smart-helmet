# Smart-helmet
This project has the following features:
1. Bike doesnot start if alcohol is detected. An alert message is sent via blynk IOT
2. Bike doesnot start if helmet not worn
3. Oled display shows the proximity of other vehicles if very near to protect the rider.
4. If fall is detected, a notification is sent to the saved contact of the rider via blynk
5. The gps location of the rider is also sent.
Sensors and microcontrollers used:
1. MQ3(Alcohol detection)
2. I2C OLED display - 2
3. MPU6050 accelerometer + gyroscope
4. FSR sensor
5. Relay
6. Ultrasonic sensors - 3
7. ESP 32 module - 2
8. relay
Working: The ESP32 present in helmet collects all data from the sensors and sends to the Blynk app via API and the necessary data to another esp32 which is connected via internet to a Second esp32 present in the bike end to cutoff powe if trigger received.
