import cv2 as cv
import numpy as np
import os
from pathlib import Path

# 在这里设置你的图像文件路径
ROOT = Path(__file__).resolve().parent
path = [
    {
        "name": "组1",
        "base": str(ROOT / "pic" / "myself.webp"),    # 相对路径: pic/myself.webp
        "overlay": str(ROOT / "pic" / "p1.png")  # 相对路径: pic/p1.png
    },
    {
        "name": "组2", 
        "base": str(ROOT / "pic" / "myself.webp"),    # 相对路径: pic/myself.webp
        "overlay": str(ROOT / "pic" / "p2.png")  # 相对路径: pic/p2.png
    },
    {
        "name": "组3",
        "base": str(ROOT / "pic" / "myself.webp"),    # 相对路径: pic/myself.webp
        "overlay": str(ROOT / "pic" / "p3.png")  # 相对路径: pic/p3.png
    }
]

def load_image_groups():
    """加载本地图像组"""
    groups = []
    
    for img_info in path:
        base_img = cv.imread(img_info["base"])
        overlay_img = cv.imread(img_info["overlay"])
        
        # 统一尺寸
        h = min(base_img.shape[0], overlay_img.shape[0])
        w = min(base_img.shape[1], overlay_img.shape[1])
        base_img = cv.resize(base_img, (w, h))
        overlay_img = cv.resize(overlay_img, (w, h))
        
        groups.append({
            "name": img_info["name"],
            "base": base_img,
            "overlay": overlay_img
        })
    
    return groups

def blend_with_overlay(base, overlay, overlay_alpha):
    """正确的融合方式：底片100% + 覆盖层透明度"""
    # 将覆盖层转换为浮点数并应用透明度
    overlay_float = overlay.astype(np.float32)
    base_float = base.astype(np.float32)
    
    # 覆盖层透明度 (0=完全透明，1=完全不透明)
    alpha = overlay_alpha / 100.0
    
    # 融合公式：result = base + (overlay - base) * alpha
    # 这样当alpha=1时，result = overlay；当alpha=0时，result = base
    result_float = base_float + (overlay_float - base_float) * alpha
    
    # 确保值在0-255范围内
    result_float = np.clip(result_float, 0, 255)
    
    return result_float.astype(np.uint8)

def main():
    groups = load_image_groups()
    current_group = 0
    overlay_alpha = 0  # 覆盖层透明度
    
    cv.namedWindow("Image Blending")
    cv.createTrackbar('Overlay', 'Image Blending', overlay_alpha, 100, lambda x: None)
    
    print("A/D: Switch Group | Q: Quit")
    print("Slider: 0=Base only, 100=Overlay only")
    
    while True:
        group = groups[current_group]
        overlay_alpha = cv.getTrackbarPos('Overlay', 'Image Blending')
        
        # 使用正确的融合方法
        result = blend_with_overlay(group["base"], group["overlay"], overlay_alpha)
        
        # 显示信息
        cv.putText(result, f"Group:{group['name']}", (10, 30), 
                  cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv.putText(result, f"Overlay:{overlay_alpha}%", (10, 60), 
                  cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv.imshow("Image Blending", result)
        
        key = cv.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        if key == ord('a'):
            current_group = (current_group - 1) % len(groups)
        if key == ord('d'):
            current_group = (current_group + 1) % len(groups)
    
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()