from ultralytics import YOLO
import cv2
import numpy as np

# ================== 路径 ==================
MODEL_PATH = r"D:\YOLO\corn\code\runs\train\corn_leaf9\weights\best.pt"
IMAGE_PATH = r"D:\YOLO\corn\玉米图像数据集\77张图片_mmexport1776070929550.,\mmexport1776063821672..jpg"

# ================== 参数 ==================
CONF_THRES = 0.25   # ⭐关键：和YOLO一致
MIN_AREA = 2000     # ⭐过滤异常大/小框

# ================== 加载模型 ==================
model = YOLO(MODEL_PATH)

# ================== 推理 ==================
results = model(IMAGE_PATH, conf=CONF_THRES)[0]

# 读取图片
img = cv2.imread(IMAGE_PATH)

# ================== 获取最终检测结果 ==================
boxes = results.boxes.xyxy.cpu().numpy()
confs = results.boxes.conf.cpu().numpy()

# ================== 过滤异常框 ==================
filtered_boxes = []

for box, conf in zip(boxes, confs):
    x1, y1, x2, y2 = box
    area = (x2 - x1) * (y2 - y1)

    if area > MIN_AREA:   # 过滤太小噪声
        filtered_boxes.append(box)

# ================== 如果没有检测到 ==================
if len(filtered_boxes) == 0:
    print("❌ 没有检测到叶片")
    cv2.imwrite("result.jpg", img)
    exit()

# ================== 计算中心点 ==================
centers = []
for box in filtered_boxes:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    centers.append([cx, cy])

centers = np.array(centers)

# ================== 主茎方向（PCA） ==================
if len(filtered_boxes) >= 2:
    mean = np.mean(centers, axis=0)
    cov = np.cov(centers - mean, rowvar=False)
    eigvals, eigvecs = np.linalg.eig(cov)
    main_vec = eigvecs[:, np.argmax(eigvals)]

    proj_list = []

    for box, center in zip(filtered_boxes, centers):
        proj = np.dot(center - mean, main_vec)
        proj_list.append((box, proj))

    # 从下到上排序
    sorted_boxes = sorted(proj_list, key=lambda x: x[1], reverse=True)

else:
    # 只有一个叶片
    sorted_boxes = [(filtered_boxes[0], 0)]

# ================== 画框 + 编号 ==================
for i, (box, _) in enumerate(sorted_boxes):
    x1, y1, x2, y2 = map(int, box)

    # 画框（绿色）
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # 编号（红色）
    cv2.putText(img, str(i+1), (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

# ================== 保存 ==================
cv2.imwrite("result.jpg", img)

print("✅ 完成：稳定检测 + 主茎排序 + 编号")