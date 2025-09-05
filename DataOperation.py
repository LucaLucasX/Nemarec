import os
import shutil
import random

# 原始 train + val 数据目录（你当前的结构）
SRC_ROOT = r'E:\Data'
# 合并后的统一目录
ALL_DATA_DIR = os.path.join(SRC_ROOT, 'all_data')
# 新的划分目录
TRAIN_DIR = os.path.join(SRC_ROOT, 'train')
VAL_DIR = os.path.join(SRC_ROOT, 'valid')

# 类别列表
class_mapping = (
    'Acrobeles', 'Acrobeloides', 'Amplimerlinius', 'Aphelenchoides', 'Aporcelaimus',
    'Axonchium', 'Discolimus', 'Ditylenchus', 'Dorylaimus', 'Eudorylaimus',
    'Helicotylenchus', 'Mesodorylaimus', 'Miconchus', 'Mylonchulus', 'Panagrolaimus',
    'Pratylenchus', 'Pristionchus', 'Rhbiditis', 'Xenocriconema'
)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def merge_all_data():
    print("🔄 合并所有 train + val 到 all_data...")
    for cls in class_mapping:
        merged_class_dir = os.path.join(ALL_DATA_DIR, cls)
        ensure_dir(merged_class_dir)
        total = 0

        for subfolder in ['train', 'valid']:
            src_cls_dir = os.path.join(SRC_ROOT, subfolder, cls)
            if not os.path.exists(src_cls_dir):
                print(f"⚠️ 警告：目录不存在 {src_cls_dir}")
                continue

            for filename in os.listdir(src_cls_dir):
                src_path = os.path.join(src_cls_dir, filename)
                dst_path = os.path.join(merged_class_dir, filename)
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
                    total += 1
        print(f"✅ 类别 {cls} 合并完成，共 {total} 个样本")

def split_dataset():
    print("\n🔀 开始按 7:3 重新划分训练集和验证集...")
    for cls in class_mapping:
        all_cls_dir = os.path.join(ALL_DATA_DIR, cls)
        if not os.path.exists(all_cls_dir):
            print(f"⚠️ 警告：缺少类别目录 {all_cls_dir}，跳过")
            continue

        images = [f for f in os.listdir(all_cls_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.tif', '.tiff'))]
        total = len(images)
        if total == 0:
            print(f"⚠️ 类别 {cls} 没有图片，跳过")
            continue

        random.shuffle(images)
        split_idx = int(0.7 * total)
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]

        train_cls_dir = os.path.join(TRAIN_DIR, cls)
        val_cls_dir = os.path.join(VAL_DIR, cls)
        ensure_dir(train_cls_dir)
        ensure_dir(val_cls_dir)

        for img in train_imgs:
            src_path = os.path.join(all_cls_dir, img)
            dst_path = os.path.join(train_cls_dir, img)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
            else:
                print(f"❌ 跳过不存在的文件: {src_path}")

        for img in val_imgs:
            src_path = os.path.join(all_cls_dir, img)
            dst_path = os.path.join(val_cls_dir, img)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
            else:
                print(f"❌ 跳过不存在的文件: {src_path}")

        print(f"✅ 类别 {cls} 划分完成：训练 {len(train_imgs)}，验证 {len(val_imgs)}")

if __name__ == "__main__":
    # 第一步：合并原始数据
    # merge_all_data()
    # 第二步：划分训练和验证集
    split_dataset()
    print("\n🎉 完成所有数据整理！可以开始训练啦。")
