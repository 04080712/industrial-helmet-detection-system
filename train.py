from ultralytics import YOLO

# carregar modelo base
model = YOLO("yolov8s.pt")

# treinar usando o dataset
model.train(
    data="data.yaml",
    epochs=80,
    imgsz=640
)