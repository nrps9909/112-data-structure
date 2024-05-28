import asyncio
import os
import cv2
import time
from ultralytics import YOLO
import supervision as sv
import numpy as np
import globals

# 获取项目根目录并构建模型文件路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
model_path = os.path.join(project_root, 'assets', 'best.pt')

# 加载 YOLO 模型
model = YOLO(model_path)

async def object_detection():
    polygons = np.array([
        [213, 130],
        [426, 130],
        [426, 350],
        [213, 350]
    ])
    globals.counter_drink = 0
    detection_start_time = None
    total_detection_time = 0
    detection_period_start = time.time()
    cap = cv2.VideoCapture(0)
    assert cap.isOpened(), "Cannot open camera"
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    zones = sv.PolygonZone(polygon=polygons)
    zone_annotators = sv.PolygonZoneAnnotator(zone=zones, color=sv.Color.RED, thickness=2, text_thickness=2, text_scale=1)
    box_annotators = sv.BoxAnnotator(thickness=3, text_thickness=1, text_scale=1)

    while not globals.stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, imgsz=640)[0]
        detections = sv.Detections.from_ultralytics(results)
        mask = zones.trigger(detections=detections)
        detections = detections[(detections.class_id == 0) & (detections.confidence > 0.1) & mask]

        current_time = time.time()

        if len(detections) > 0:
            if detection_start_time is None:
                detection_start_time = current_time
            total_detection_time += current_time - detection_start_time
            detection_start_time = current_time

        labels = [f"{results.names[class_id]}: {confidence:.2f}" for class_id, confidence in zip(detections.class_id, detections.confidence)]
        frame = box_annotators.annotate(scene=frame, detections=detections, labels=labels)
        frame = zone_annotators.annotate(scene=frame)
        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) == ord('q'):
            break

        await asyncio.sleep(0.01)

        if current_time - detection_period_start >= 10:
            if total_detection_time <= 3:
                globals.counter_drink += 1
            total_detection_time = 0
            detection_start_time = None
            detection_period_start = current_time

    cap.release()
    cv2.destroyAllWindows()
    print("Object detection stopped.")

if __name__ == "__main__":
    # 初始化全局停止事件
    globals.stop_event = asyncio.Event()

    # 运行对象检测
    try:
        asyncio.run(object_detection())
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught, stopping object detection...")
        globals.stop_event.set()
        print("Object detection stopped gracefully.")
