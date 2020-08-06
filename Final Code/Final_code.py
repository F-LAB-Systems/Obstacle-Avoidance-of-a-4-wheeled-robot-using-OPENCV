import cv2
import numpy as np
import math
import os

testmode = 1  # To display images to verify. Set to zero if not intrested in displaying images.


# make_chunks function creats chunks.
# inputs -- EdgeArray and the size_of_chunk to create.
# output -- yield successive n-sized chunks.
def make_chunks(EdgeArray, size_of_chunk):
    chunks = []
    for i in range(0, len(EdgeArray), size_of_chunk):
        chunks.append(EdgeArray[i:i + size_of_chunk])
    return chunks


# Code to draw edge representation.

cap = cv2.VideoCapture(0)  # Creating object to capturing frame from inbult camera(0) or the external camera(1)
StepSize = 5
while (1):
    _, frame = cap.read()  # Reading the frame from the object.

    original_frame = frame.copy()  # Copy of frame which will be used for to compare with other images after appling various operations.
    img_edgerep = frame.copy()  # Copy of frame which will be used for edge representation.
    img_contour = frame.copy()  # Copy of frame which will be used for drawing contours.
    img_navigation = frame.copy()  # Copy of frame which will be used for indicating direction of navigation.

    blur = cv2.bilateralFilter(img_edgerep, 9, 40, 40)  # Blurring the image to remove the noise present in the image.
    edges = cv2.Canny(blur, 50, 100)  # Obtaining clear edges using canny edge detector.

    img_edgerep_h = img_edgerep.shape[0] - 1  # Storing the height of the image which will be used in for loop.
    img_edgerep_w = img_edgerep.shape[1] - 1  # Storing the width of the image which will be used in for loop.

    EdgeArray = []  # Initilizing the array to store the concerned edges for edge representation.

    for j in range(0, img_edgerep_w, StepSize):  # FOR loop along the width of the image with given stepsize.
        pixel = (j, 0)  # If no edge found in column this value will be stored in edgearray.
        for i in range(img_edgerep_h - 5, 0, -1):  # FOR loop along the height of the image.
            if edges.item(i, j) == 255:  # Checking for edges.
                pixel = (j, i)
                break  # If edge is found break and go for the next colomn.
        EdgeArray.append(pixel)  # Store the eged detected in EgdeArray.

    for x in range(len(
            EdgeArray) - 1):  # Joining each edge to diferentiate the frame into free space and conjusted space(with objects)
        cv2.line(img_edgerep, EdgeArray[x], EdgeArray[x + 1], (0, 255, 0), 1)

    for x in range(len(
            EdgeArray)):  # Joining each point in the EdgeArray to the respective bottom edge of the frame to represent free space for the bot to move around
        cv2.line(img_edgerep, (x * StepSize, img_edgerep_h), EdgeArray[x], (0, 255, 0), 1)

    # Code to draw contours.

    blurred_frame = cv2.bilateralFilter(img_contour, 9, 75, 75)
    gray = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 106, 255, 1)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img_edgerep, contours, -1, (0, 0, 255), 3)

    # Code to decide direction of navigation

    number_of_chunks = 3
    size_of_chunk = int(len(EdgeArray) / number_of_chunks)
    chunks = make_chunks(EdgeArray, size_of_chunk)  # Calling make_chunks function to create the chunks.
    avg_of_chunk = []
    for i in range(len(chunks) - 1):
        x_vals = []
        y_vals = []
        for (x, y) in chunks[i]:  # Storing the x and y value saperatly to find average.
            x_vals.append(x)
            y_vals.append(y)
        avg_x = int(np.average(x_vals))
        avg_y = int(np.average(y_vals))
        avg_of_chunk.append([avg_y, avg_x])
        cv2.line(frame, (int(img_edgerep_w / 2), img_edgerep_h), (avg_x, avg_y), (255, 0, 0),
                 2)  # Draw lines to each average chunks to decide the direction of navigation.

    forwardEdge = avg_of_chunk[1]
    cv2.line(frame, (int(img_edgerep_w / 2), img_edgerep_h), (forwardEdge[1], forwardEdge[0]), (0, 255, 0), 3)
    farthest_point = (min(avg_of_chunk))
    # print(farthest_point)

    if forwardEdge[0] > 250:  # Checking for the object at the front is close to bot.
        if farthest_point[1] < 310:  # Checking for the farthest_point on the left of the frame.
            direction = "Move left "
            print(direction)
        else:
            direction = "Move right "
            print(direction)
    else:
        direction = "Move forward "
        print(direction)

        # Code to display the results

    if testmode == 1:
        cv2.imshow("Original_Frame", original_frame)
        cv2.imshow("Canny", edges)
        cv2.imshow("Threshold", thresh)
        cv2.imshow("Edge_separation", img_edgerep)
        font = cv2.FONT_HERSHEY_SIMPLEX
        navigation = cv2.putText(frame, direction, (275, 50), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow("Navigation", navigation)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows
cap.release()