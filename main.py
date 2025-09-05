import torch
from torchvision import datasets, models, transforms
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
from cv2 import imread, cvtColor, COLOR_RGB2BGR
from PIL import Image
from tqdm import tqdm
import time

# 参数配置
dataset_path = r'/root/autodl-tmp/Data'
save_model_name = "vit"  # 'resnet101' 或 'vit'
num_classes = 19
batch_size = 128
num_epochs = 50
# 模式选择：train 或 val
mode = "train"  # 或 "val"
np.random.seed(0)

# 自定义 GaussianBlur 数据增强
class GaussianBlur(object):
    def __init__(self, kernel_size, min=0.1, max=2.0):
        self.min = min
        self.max = max
        self.kernel_size = kernel_size

    def __call__(self, sample):
        sample = np.array(sample)
        if np.random.random_sample() < 0.5:
            sigma = (self.max - self.min) * np.random.random_sample() + self.min
            sample = cv2.GaussianBlur(sample, (self.kernel_size, self.kernel_size), sigma)
        return sample

# 数据增强
image_transforms = {
    'train': transforms.Compose([
        transforms.ColorJitter(0.2, 0.2, 0.2, 0.2),
        transforms.RandomHorizontalFlip(p=0.7),
        transforms.RandomVerticalFlip(p=0.7),
        transforms.Resize((224, 224)),
        GaussianBlur(kernel_size=21),
        transforms.ToTensor()
    ]),
    'valid': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
}

# 自定义 Dataset
class NemaLoader(Dataset):
    def __init__(self, dataset, train, transform):
        self.dataset = dataset.imgs
        self.targets = np.asarray(dataset.targets)
        self.transform = transform
        self.isTrain = train

    def _getImage(self, path):
        import os
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        try:
            img = Image.open(path).convert('RGB')
        except Exception as e:
            raise ValueError(f"PIL failed to load image: {path}, error: {e}")
        return np.array(img)

    def __getitem__(self, index):
        img_path, label = self.dataset[index]
        img = self._getImage(img_path)
        img = Image.fromarray(img, mode='RGB')
        return self.transform(img), label  # 无论训练还是验证，都只返回一个增强版本
    

    def __len__(self):
        return len(self.targets)

# 设备
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

# 加载数据
train_directory = os.path.join(dataset_path, 'train')
valid_directory = os.path.join(dataset_path, 'valid')

data = {
    'train': datasets.ImageFolder(root=train_directory),
    'valid': datasets.ImageFolder(root=valid_directory)
}

train_data = DataLoader(NemaLoader(data['train'], True, image_transforms['train']),
                        batch_size=batch_size, shuffle=True)
valid_data = DataLoader(NemaLoader(data['valid'], False, image_transforms['valid']),
                        batch_size=batch_size, shuffle=False)

train_size = len(data['train'])
valid_size = len(data['valid'])
print(f"Train size: {train_size}, Valid size: {valid_size}")

# 模型加载
if save_model_name == "resnet101":
    model = models.resnet101(pretrained=(mode == "train"))  # 训练时用官方预训练，验证则跳过
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    if mode == "val":
        # 仅验证阶段加载你训练好的模型参数
        pthfile = 'resnet101_data_expansion_3x_best_model_parameters.pt'
        model_PT = torch.load(pthfile, map_location=device)
        model.load_state_dict(model_PT["model_state_dict"])

elif save_model_name == "vit":
    model = models.vit_b_16(pretrained=False)  # 不用官方预训练（你有自己的预训练权重）

    if mode == "train":
        # 训练时加载预训练权重
        vit_weights_path = "vit_b_16-c867db91.pth"
        state_dict = torch.load(vit_weights_path, map_location=device)

        if "model_state_dict" in state_dict:
            state_dict = state_dict["model_state_dict"]

        model.load_state_dict(state_dict, strict=True)

    elif mode == "val":
        # 验证时加载你训练好的模型权重
        pthfile = 'vit_best_model.pt'
        state_dict = torch.load(pthfile, map_location=device)
        model.load_state_dict(state_dict["model_state_dict"])

    # 替换分类头
    if isinstance(model.heads, nn.Sequential):
        old_head = model.heads[-1]
        in_features = old_head.in_features
        model.heads[-1] = nn.Linear(in_features, num_classes)
    else:
        raise ValueError("Unexpected model.heads structure")

else:
    raise ValueError("Unsupported model name")

model = model.to(device)
print("模型加载完毕")
# 损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer_ft = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9, weight_decay=0.01)

# 训练一个epoch
def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    running_acc = 0.0
    total_samples = 0

    for data1, data2, target1, target2 in dataloader:
        data = torch.cat([data1, data2])
        target = torch.cat([target1, target2])
        inputs, labels = data.to(device), target.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
        acc = (outputs.argmax(1) == labels).float().sum()
        running_acc += acc.item()
        total_samples += inputs.size(0)

    avg_loss = running_loss / total_samples
    avg_acc = running_acc / total_samples
    return avg_loss, avg_acc

# 验证一个epoch
def validate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    running_acc = 0.0
    total_samples = 0

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * inputs.size(0)
            acc = (outputs.argmax(1) == labels).float().sum()
            running_acc += acc.item()
            total_samples += inputs.size(0)

    avg_loss = running_loss / total_samples
    avg_acc = running_acc / total_samples
    return avg_loss, avg_acc

# 训练与验证函数
def train_and_valid(model, criterion, optimizer, train_loader, valid_loader, epochs=50):
    best_acc = 0.0
    best_epoch = 0
    history = []

    for epoch in range(epochs):
        epoch_start = time.time()
        print(f"\nEpoch {epoch+1}/{epochs}")

        # === 训练阶段 ===
        model.train()
        running_loss = 0.0
        running_corrects = 0
        total = 0

        train_bar = tqdm(train_loader, desc='Training', leave=False)
        for inputs, labels in train_bar:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            _, preds = torch.max(outputs, 1)
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            total += labels.size(0)

            train_bar.set_postfix(loss=loss.item())

        train_loss = running_loss / total
        train_acc = running_corrects.double().item() / total

        # === 验证阶段 ===
        valid_loss, valid_acc = validate(model, valid_loader, criterion, device)

        history.append([train_loss, valid_loss, train_acc, valid_acc])

        # 保存最优模型
        if valid_acc > best_acc:
            best_acc = valid_acc
            best_epoch = epoch + 1
            torch.save(model.state_dict(), f'{save_model_name}-best-model.pt')

        # 显示当前 epoch 信息
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} | "
              f"Valid Loss: {valid_loss:.4f}, Valid Acc: {valid_acc:.4f} | "
              f"Time: {time.time() - epoch_start:.2f}s")

    print(f"\n🎯 Best Valid Acc: {best_acc:.4f} at epoch {best_epoch}")
    return model, history

# _,acc = validate(model,valid_data,criterion,device)
# print(acc)

trained_model, history = train_and_valid(model, criterion, optimizer_ft, train_data, valid_data, num_epochs)

# 保存最终模型
torch.save(trained_model.state_dict(), f'model_{save_model_name}_final.pt')

# 绘制 Loss 和 Accuracy 曲线
history = np.array(history)

plt.figure()
plt.plot(history[:, 0], label='Train Loss')
plt.plot(history[:, 1], label='Val Loss')
plt.legend()
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Loss Curve')
plt.savefig(f'{dataset_path}/loss_curve_{save_model_name}.png')
plt.show()

plt.figure()
plt.plot(history[:, 2], label='Train Acc')
plt.plot(history[:, 3], label='Val Acc')
plt.legend()
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Accuracy Curve')
plt.savefig(f'{dataset_path}/accuracy_curve_{save_model_name}.png')
plt.show()
