from ultralytics import YOLO
import cv2
import numpy as np
import sys
from pathlib import Path

# ================== 路径 ==================
MODEL_PATH = r"D:\YOLO\corn\code\runs\train\corn_leaf10\weights\best.pt"
DEFAULT_IMAGE_PATH = r"D:\YOLO\corn\pic2\微信图片_20260414185925_495_6.jpg"
IMAGE_PATH = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IMAGE_PATH
# ================== 参数 ==================
CONF_THRES = 0.15  # ⭐关键：和YOLO一致
MIN_AREA = 2000     # ⭐过滤异常大/小框
DUPLICATE_IOU_THRES = 0.35
OUTPUT_PATH = str(Path(IMAGE_PATH).with_name("result.jpg"))

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
filtered_confs = []

for box, conf in zip(boxes, confs):
    x1, y1, x2, y2 = box
    area = (x2 - x1) * (y2 - y1)

    if area > MIN_AREA:   # 过滤太小噪声
        filtered_boxes.append(box)
        filtered_confs.append(float(conf))


def box_iou(box_a, box_b):
    """计算两个框的 IoU。"""
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)

    union_area = area_a + area_b - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def suppress_duplicate_boxes(box_list, conf_list, iou_thres):
    """按置信度从高到低保留框，去掉和已保留框高度重叠的重复检测。"""
    if not box_list:
        return [], []

    order = sorted(range(len(box_list)), key=lambda idx: conf_list[idx], reverse=True)
    kept_boxes = []
    kept_confs = []

    for idx in order:
        current_box = box_list[idx]
        duplicate = False

        for kept_box in kept_boxes:
            if box_iou(current_box, kept_box) >= iou_thres:
                duplicate = True
                break

        if not duplicate:
            kept_boxes.append(current_box)
            kept_confs.append(conf_list[idx])

    return kept_boxes, kept_confs


filtered_boxes, filtered_confs = suppress_duplicate_boxes(
    filtered_boxes,
    filtered_confs,
    DUPLICATE_IOU_THRES,
)

# 如果没有检测到 
if len(filtered_boxes) == 0:
    print("没有检测到叶片")
    cv2.imwrite(OUTPUT_PATH, img)
    exit()

# 计算中心点
centers = []
for box in filtered_boxes:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    centers.append([cx, cy])

centers = np.array(centers, dtype=np.float32)


def sort_bottom_to_top(box_list, center_list):
    """按叶片从下到上的顺序排序。

    这里直接以中心点的纵坐标为主，不再按左右主轴排序，避免先识别一边。
    """
    if len(box_list) <= 1:
        return [(box_list[0], 0.0, center_list[0])]

    ordered_items = []
    for box, center in zip(box_list, center_list):
        cx, cy = float(center[0]), float(center[1])
        ordered_items.append((box, cy, cx, center))

    # 先按 y 从大到小排，保证从图像底部往顶部编号；同一水平附近再按 x 稳定排序
    ordered_items.sort(key=lambda item: (-item[1], item[2]))

    return [(box, score, center) for box, score, _, center in ordered_items]


sorted_boxes = sort_bottom_to_top(filtered_boxes, centers)

# ================== 画框 + 编号 ==================
leaf_count = len(sorted_boxes)

for i, (box, _, _) in enumerate(sorted_boxes):
    x1, y1, x2, y2 = map(int, box)

    # 画框（绿色）
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # 编号（红色）
    cv2.putText(img, str(i+1), (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

# 左上角显示总数
cv2.putText(img, f"Count: {leaf_count}", (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

# ================== 保存 ==================
cv2.imwrite(OUTPUT_PATH, img)

print(f"✅ 完成：检测到 {leaf_count} 片叶子，已按从下到上编号")
print(f"RESULT_IMAGE={OUTPUT_PATH}")