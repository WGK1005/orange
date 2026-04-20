from ultralytics import YOLO
import torch

def main():
    print("GPU是否可用:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU型号:", torch.cuda.get_device_name(0))

    model = YOLO("yolov8s.pt")

    model.train(
        data="D:\\YOLO\\corn\\corn-leaf.v1i.yolov8\\data.yaml",
        epochs=150,
        imgsz=960,
        batch=8,
        device=0,
        workers=4,
        cache=True,
        project="runs/train",
        name="corn_leaf"
    )

# ⭐⭐⭐ 关键就在这里！！！
if __name__ == '__main__':
    main()