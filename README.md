# 玉米叶片检测与图像处理项目 (Corn Leaf Detection Project)

本项目主要包含基于 YOLO 系列模型的玉米叶片目标检测代码、模型架构测试脚本以及相关的图像处理工具。

## 📂 目录结构 (code 文件夹)

- **`Test1.py`** / **`Test2.py`**: YOLO 模型推理与测试脚本。包含加载训练好的模型（如 `corn_leaf9/weights/best.pt`）、图像预处理、异常框过滤及中心点计算等功能。
- **`cv_work.py`**: 基于 OpenCV 的图像处理工具，支持图像融合、多层叠加及尺寸统一化处理。
- **`score.c`** / **`test.c`**: 项目中使用的 C 语言基础功能测试或性能评估脚本。
- **`yolo11n.pt`** / **`yolov8n.pt`** / **`yolov8s.pt`**: 预训练生成的 YOLO 模型权重文件，涵盖了从 YOLOv8 到 YOLO11 的不同版本。
- **`runs/`**: 包含模型训练 (`train`) 和推理 (`predict`) 的所有输出结果。
    - `train/corn_leaf*`: 记录了多次玉米叶片训练的日志、权重和评估图表。
    - `predict/`: 存储模型在测试集或单张图片上的检测可视化结果。

## 🚀 快速开始

### 1. 环境准备
确保已安装 `ultralytics` 和 `opencv-python`:
```bash
pip install ultralytics opencv-python
```

### 2. 模型推理
使用 `Test2.py` 来运行检测：
```python
# 修改 Test2.py 中的模型和图片路径
MODEL_PATH = "runs/train/corn_leaf9/weights/best.pt"
IMAGE_PATH = "path/to/your/image.jpg"
```

### 3. 图像处理
使用 `cv_work.py` 进行多图融合处理：
- 配置 `path` 列表中的底图与覆盖图路径即可。

## 📊 训练记录
目前已进行多次迭代（`corn_leaf` 至 `corn_leaf9`），最新的模型权重存放在 `code/runs/train/corn_leaf9/weights/best.pt`。

---
*注：本项目开发环境建议使用 Conda (yolov8 环境)。*
