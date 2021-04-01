import cv2
import math
from networktables import NetworkTables

if __name__ == '__main__':
	green_lower = (60, 20, 230)
	green_upper = (95, 255, 255)

	cap = cv2.VideoCapture(0)

	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

	NetworkTables.initialize(server='roborio-4795-frc.local')
	sd = NetworkTables.getTable('SmartDashboard') # slow

	while True:
		frame = cap.read()[1]

		if frame is None:
			break

		blurred = cv2.bilateralFilter(frame, 5, 50, 150)

		hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

		mask = cv2.inRange(hsv, green_lower, green_upper)
		mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, (5, 5))

		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
		options = []

		for cnt in cnts:
			x, y, w, h = cv2.boundingRect(cnt)

			if w > 10 and h > 2 and w > h * 2 and h * 8 > w:
				options.append(cnt)

		if len(options) > 0:
			cnt = max(options, key=cv2.contourArea)

			x, y, w, h = cv2.boundingRect(cnt)

			distance = 1.85 ** math.log(h / height, 0.6) / 12
			angle = ((x + x + w) / 2 - width / 2) / width * 2 / distance * 175

			cv2.rectangle(frame, (x, y, w, h), (0, 0, 255), 3)
			cv2.putText(frame, str(round(distance, 2)) + ' feet, ' + str(round(angle, 2)) + ' degrees', (x, y), 0, 1.25e-3 * width, (0, 255, 255), 2)
			
			sd.putNumber('goal_distance', distance)
			sd.putNumber('goal_angle', angle)
		else:
			sd.putNumber('goal_distance', -1)
			sd.putNumber('goal_angle', 0)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

		cv2.imshow('Frame', frame)

	cv2.destroyAllWindows()
