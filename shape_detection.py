import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ---  Preprocess the image ---
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)

    # --- Find contours (potential shapes) ---
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # --- Loop through each contour ---
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            # skip small noise contours
            continue

        # ---  Simplify shape ---
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        x, y, w, h = cv2.boundingRect(approx)

        # --- Classify shape ---
        shape = "Unknown"
        vertices = len(approx)
        if vertices == 3:
            shape = "Triangle"
            color = (0, 255, 0)
        elif vertices == 4:
            ratio = w / float(h)
            shape = "Square" if 0.95 <= ratio <= 1.05 else "Rectangle"
            color = (255, 0, 0)
        elif vertices > 6:
            shape = "Circle"
            color = (0, 0, 255)
        else:
            color = (200, 200, 200)

        # ---Draw on frame ---
        cv2.drawContours(frame, [approx], -1, color, 2)
        cv2.putText(frame, shape, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # --- Display result ---
    cv2.imshow("Shape Detection", frame)

    # --- 9. Exit when 'q' pressed ---
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
