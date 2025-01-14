# -*- coding: utf-8 -*-
"""FGSM sel.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/117j2P6GUS73sdz9VBQRE20oc1dhlgHsb

# 선택적으로 FGSM 공격 진행하기

필요한 라이브러리 임포트
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt

"""1. 이미지 로드 및 전처리"""

def load_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    image = Image.open(image_path).convert("RGB")
    return transform(image).unsqueeze(0)  # 배치 차원 추가

"""2. FGSM 공격 코드"""

def fgsm_attack(model, image, label, epsilon):
    image.requires_grad = True
    outputs = model(image)
    loss = nn.CrossEntropyLoss()(outputs, label)
    model.zero_grad()
    loss.backward()
    data_grad = image.grad.data
    perturbed_image = image + epsilon * data_grad.sign()
    return torch.clamp(perturbed_image, 0, 1), data_grad

"""3. 특정 영역에만 노이즈 적용하기"""

def apply_noise_to_regions(image, noise, region="full"):
    perturbed_image = image.clone()  # 원본 이미지 복사
    _, _, height, width = image.shape

    if region == "full":
        perturbed_image += noise
    elif region == "top_left":
        perturbed_image[:, :, :height // 2, :width // 2] += noise[:, :, :height // 2, :width // 2]
    elif region == "top_right":
        perturbed_image[:, :, :height // 2, width // 2:] += noise[:, :, :height // 2, width // 2:]
    elif region == "bottom_left":
        perturbed_image[:, :, height // 2:, :width // 2] += noise[:, :, height // 2:, :width // 2]
    elif region == "bottom_right":
        perturbed_image[:, :, height // 2:, width // 2:] += noise[:, :, height // 2:, width // 2:]
    elif region == "center":
        center_h, center_w = height // 4, width // 4
        perturbed_image[:, :, center_h:3 * center_h, center_w:3 * center_w] += noise[:, :, center_h:3 * center_h, center_w:3 * center_w]
    elif region == "border":
        perturbed_image[:, :, :10, :] += noise[:, :, :10, :]  # 상단 테두리
        perturbed_image[:, :, -10:, :] += noise[:, :, -10:, :]  # 하단 테두리
        perturbed_image[:, :, :, :10] += noise[:, :, :, :10]  # 왼쪽 테두리
        perturbed_image[:, :, :, -10:] += noise[:, :, :, -10:]  # 오른쪽 테두리

    return torch.clamp(perturbed_image, 0, 1)

"""4. 시각화 함수"""

def plot_images(original, noise, perturbed):
    original = original.squeeze().permute(1, 2, 0).detach().numpy()
    noise = noise.squeeze().permute(1, 2, 0).detach().numpy()
    perturbed = perturbed.squeeze().permute(1, 2, 0).detach().numpy()

    plt.figure(figsize=(12, 8))
    plt.subplot(1, 3, 1)
    plt.title("Original Image")
    plt.imshow(original)
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.title("Noise")
    plt.imshow(noise, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.title("Perturbed Image")
    plt.imshow(perturbed)
    plt.axis('off')

    plt.show()

"""5. 메인 코드 실행"""

if __name__ == "__main__":
    # 모델 정의 (Pretrained 모델 사용)
    from torchvision.models import resnet18
    model = resnet18(pretrained=True)
    model.eval()

    # 이미지 로드
    image_path = './John von neumann.jpg'
    image = load_image(image_path)

    # 임의의 라벨 설정 (0번 클래스 예시)
    label = torch.tensor([0])

    # FGSM 공격 실행
    epsilon = 0.1  # 노이즈 강도
    perturbed_image, noise = fgsm_attack(model, image, label, epsilon)

    # 노이즈 적용할 영역들
    regions = ["full", "top_left", "top_right", "bottom_left", "bottom_right", "center", "border"]

    # 각 영역에 대해 노이즈 적용 및 시각화
    for region in regions:
        print(f"Applying noise to region: {region}")
        region_perturbed_image = apply_noise_to_regions(image, noise.sign() * epsilon, region)
        plot_images(image, noise.sign() * epsilon, region_perturbed_image)