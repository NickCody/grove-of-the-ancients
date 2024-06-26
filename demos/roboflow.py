import cv2
import argparse

from ultralytics import YOLO
import supervision as sv
import numpy as np
from time import sleep


ZONE_POLYGON = np.array([
    [0, 0],
    [0.5, 0],
    [0.5, 1],
    [0, 1]
])


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument(
        "--webcam-resolution", 
        default=[1280, 720], 
        nargs=2, 
        type=int
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO("yolov8l.pt")

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    zone_polygon = (ZONE_POLYGON * np.array(args.webcam_resolution)).astype(int)
    zone = sv.PolygonZone(polygon=zone_polygon, frame_resolution_wh=tuple(args.webcam_resolution))
    zone_annotator = sv.PolygonZoneAnnotator(
        zone=zone, 
        color=sv.Color.red(),
        thickness=2,
        text_thickness=4,
        text_scale=2
    )

    while True:
        ret, frame = cap.read()

        result = model.predict(frame, device='mps', verbose=True)[0]
        detections = sv.Detections.from_ultralytics(result)

        vals = []
        for det in detections:
            coords, _, confidence, _, _, info = det
            x1, y1, w, h = coords
            class_name = info['class_name']
            vals.append((class_name, confidence, (x1, y1)))
            cv2.rectangle(frame, (x1, y1), (x1+w, y1+h), (0, 255, 0), 2)

        for v in vals:
            print(v)

    
        cv2.imshow("yolov8", frame)

        # Sleep for 100ms
        sleep(0.1)

        if (cv2.waitKey(30) == 27):
            break


if __name__ == "__main__":
    main()