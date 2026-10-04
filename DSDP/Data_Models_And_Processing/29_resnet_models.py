"""
ResNet 模型架構

實現 5 個 ResNet 變體：
1. Baseline ResNet (3 blocks, 128 hidden, ReLU)
2. Deep ResNet (6 blocks, 128 hidden, ReLU)
3. Wide ResNet (3 blocks, 256 hidden, ReLU)
4. LeakyReLU ResNet (3 blocks, 128 hidden, LeakyReLU)
5. GELU ResNet (3 blocks, 128 hidden, GELU)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ResNetBlock(nn.Module):
    """ResNet 殘差塊"""
    
    def __init__(self, in_features, out_features, activation='relu', dropout=0.2):
        super(ResNetBlock, self).__init__()
        
        self.fc1 = nn.Linear(in_features, out_features)
        self.bn1 = nn.BatchNorm1d(out_features)
        
        self.fc2 = nn.Linear(out_features, out_features)
        self.bn2 = nn.BatchNorm1d(out_features)
        
        # Residual connection
        if in_features != out_features:
            self.residual_proj = nn.Linear(in_features, out_features)
        else:
            self.residual_proj = None
        
        self.dropout = nn.Dropout(dropout)
        
        # Activation function
        if activation == 'relu':
            self.activation = nn.ReLU()
        elif activation == 'leaky_relu':
            self.activation = nn.LeakyReLU(negative_slope=0.01)
        elif activation == 'gelu':
            self.activation = nn.GELU()
        else:
            raise ValueError(f"Unknown activation: {activation}")
    
    def forward(self, x):
        # Save input for residual
        residual = x
        
        # First layer
        out = self.fc1(x)
        out = self.bn1(out)
        out = self.activation(out)
        out = self.dropout(out)
        
        # Second layer
        out = self.fc2(out)
        out = self.bn2(out)
        
        # Add residual
        if self.residual_proj is not None:
            residual = self.residual_proj(residual)
        
        out += residual
        out = self.activation(out)
        
        return out

class TemporalResNet(nn.Module):
    """時序預測 ResNet 模型"""
    
    def __init__(self, input_dim, hidden_dim=128, num_blocks=3, 
                 activation='relu', dropout=0.2):
        super(TemporalResNet, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_blocks = num_blocks
        self.activation = activation
        
        # Input projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        # ResNet blocks
        self.blocks = nn.ModuleList([
            ResNetBlock(hidden_dim, hidden_dim, activation, dropout)
            for _ in range(num_blocks)
        ])
        
        # Output layer
        self.output = nn.Linear(hidden_dim, 1)
    
    def forward(self, x):
        # Input projection
        x = self.input_proj(x)
        x = F.relu(x)
        
        # ResNet blocks
        for block in self.blocks:
            x = block(x)
        
        # Output
        x = self.output(x)
        
        return x.squeeze(-1)  # (batch,)
    
    def get_model_info(self):
        """返回模型資訊"""
        return {
            'input_dim': self.input_dim,
            'hidden_dim': self.hidden_dim,
            'num_blocks': self.num_blocks,
            'activation': self.activation,
            'total_params': sum(p.numel() for p in self.parameters()),
            'trainable_params': sum(p.numel() for p in self.parameters() if p.requires_grad)
        }

def create_model_variants(input_dim):
    """創建 5 個模型變體"""
    
    variants = {
        'baseline': {
            'name': 'Baseline ResNet',
            'model': TemporalResNet(
                input_dim=input_dim,
                hidden_dim=128,
                num_blocks=3,
                activation='relu',
                dropout=0.2
            ),
            'description': '3 blocks, 128 hidden, ReLU'
        },
        'deep': {
            'name': 'Deep ResNet',
            'model': TemporalResNet(
                input_dim=input_dim,
                hidden_dim=128,
                num_blocks=6,
                activation='relu',
                dropout=0.2
            ),
            'description': '6 blocks, 128 hidden, ReLU (deeper)'
        },
        'wide': {
            'name': 'Wide ResNet',
            'model': TemporalResNet(
                input_dim=input_dim,
                hidden_dim=256,
                num_blocks=3,
                activation='relu',
                dropout=0.2
            ),
            'description': '3 blocks, 256 hidden, ReLU (wider)'
        },
        'leaky_relu': {
            'name': 'LeakyReLU ResNet',
            'model': TemporalResNet(
                input_dim=input_dim,
                hidden_dim=128,
                num_blocks=3,
                activation='leaky_relu',
                dropout=0.2
            ),
            'description': '3 blocks, 128 hidden, LeakyReLU'
        },
        'gelu': {
            'name': 'GELU ResNet',
            'model': TemporalResNet(
                input_dim=input_dim,
                hidden_dim=128,
                num_blocks=3,
                activation='gelu',
                dropout=0.2
            ),
            'description': '3 blocks, 128 hidden, GELU'
        }
    }
    
    return variants

# 測試代碼
if __name__ == '__main__':
    print("="*80)
    print("ResNet 模型架構測試")
    print("="*80)
    print()
    
    # 測試參數
    input_dim = 69  # 從特徵工程得知
    batch_size = 32
    
    print(f"輸入維度: {input_dim}")
    print(f"批次大小: {batch_size}\n")
    
    # 創建模型變體
    variants = create_model_variants(input_dim)
    
    # 測試每個變體
    for variant_name, variant_info in variants.items():
        model = variant_info['model']
        
        print(f"{variant_info['name']}:")
        print(f"  描述: {variant_info['description']}")
        
        # 模型資訊
        info = model.get_model_info()
        print(f"  參數量: {info['total_params']:,}")
        print(f"  隱藏層維度: {info['hidden_dim']}")
        print(f"  ResNet 層數: {info['num_blocks']}")
        print(f"  激活函數: {info['activation']}")
        
        # 測試前向傳播
        x = torch.randn(batch_size, input_dim)
        with torch.no_grad():
            output = model(x)
        
        print(f"  輸入形狀: {x.shape}")
        print(f"  輸出形狀: {output.shape}")
        print(f"  ✓ 前向傳播成功\n")
    
    print("="*80)
    print("✅ 模型架構測試完成！")
    print("="*80)
