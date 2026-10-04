"""
ResNet 模型訓練

訓練 5 個變體 × 3 個網格 = 15 個模型
- Weighted MSE Loss (爆量 5x 權重)
- Adam optimizer + ReduceLROnPlateau
- Early stopping (patience=25)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
import os
import time
from importlib import import_module
import sys

# 導入模型
sys.path.insert(0, os.path.dirname(__file__))
import importlib
resnet_models = importlib.import_module('29_resnet_models')
create_model_variants = resnet_models.create_model_variants

class CrowdFlowDataset(Dataset):
    """人流預測數據集"""
    
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class WeightedMSELoss(nn.Module):
    """加權 MSE Loss（爆量事件加權）"""
    
    def __init__(self, threshold, weight_burst=5.0):
        super(WeightedMSELoss, self).__init__()
        self.threshold = threshold
        self.weight_burst = weight_burst
    
    def forward(self, pred, target):
        # 計算權重
        weights = torch.where(
            target > self.threshold,
            torch.tensor(self.weight_burst),
            torch.tensor(1.0)
        ).to(pred.device)
        
        # 加權 MSE
        loss = weights * (pred - target) ** 2
        return loss.mean()

def train_epoch(model, dataloader, criterion, optimizer, device):
    """訓練一個 epoch"""
    model.train()
    total_loss = 0
    
    for X_batch, y_batch in dataloader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device)
        
        # 前向傳播
        optimizer.zero_grad()
        output = model(X_batch)
        loss = criterion(output, y_batch)
        
        # 反向傳播
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item() * len(X_batch)
    
    return total_loss / len(dataloader.dataset)

def validate(model, dataloader, criterion, device):
    """驗證"""
    model.eval()
    total_loss = 0
    
    with torch.no_grad():
        for X_batch, y_batch in dataloader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            
            output = model(X_batch)
            loss = criterion(output, y_batch)
            
            total_loss += loss.item() * len(X_batch)
    
    return total_loss / len(dataloader.dataset)

def train_model(model, train_loader, val_loader, criterion, optimizer, scheduler,
                device, max_epochs=200, patience=25, model_save_path=None):
    """訓練模型"""
    
    best_val_loss = float('inf')
    epochs_no_improve = 0
    train_losses = []
    val_losses = []
    
    print(f"  開始訓練（最多 {max_epochs} epochs，patience={patience}）...")
    
    for epoch in range(max_epochs):
        # 訓練
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        
        # 驗證
        val_loss = validate(model, val_loader, criterion, device)
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        # 學習率調度
        scheduler.step(val_loss)
        
        # 早停檢查
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_no_improve = 0
            
            # 儲存最佳模型
            if model_save_path:
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'train_loss': train_loss,
                    'val_loss': val_loss,
                }, model_save_path)
        else:
            epochs_no_improve += 1
        
        # 每10個 epoch 輸出一次
        if (epoch + 1) % 10 == 0:
            print(f"    Epoch {epoch+1:3d}: Train Loss={train_loss:.4f}, Val Loss={val_loss:.4f}, "
                  f"Best Val={best_val_loss:.4f}, LR={optimizer.param_groups[0]['lr']:.6f}")
        
        # 早停
        if epochs_no_improve >= patience:
            print(f"    早停於 epoch {epoch+1} (無改善 {patience} epochs)")
            break
    
    return {
        'train_losses': train_losses,
        'val_losses': val_losses,
        'best_val_loss': best_val_loss,
        'final_epoch': epoch + 1
    }

def main():
    print("="*80)
    print("ResNet 模型訓練")
    print("="*80)
    print()
    
    # 設備
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用設備: {device}\n")
    
    # 創建輸出目錄
    os.makedirs('resnet_models', exist_ok=True)
    os.makedirs('resnet_logs', exist_ok=True)
    
    # 選定的網格
    selected_grids = [
        {'rank': 1, 'x': 80, 'y': 95, 'feature': '最高人流'},
        {'rank': 2, 'x': 34, 'y': 44, 'feature': '最大瞬間湧入'},
        {'rank': 3, 'x': 86, 'y': 149, 'feature': '最高波動性'}
    ]
    
    # 訓練所有網格
    for grid_info in selected_grids:
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        
        print(f"{'='*80}")
        print(f"網格 #{rank}: ({x}, {y}) - {feature}")
        print(f"{'='*80}\n")
        
        # 載入數據
        data_file = f'resnet_features/grid_{rank}_{x}_{y}.npz'
        data = np.load(data_file, allow_pickle=True)
        
        X_train = data['X_train']
        X_test = data['X_test']
        y_train = data['y_train']
        y_test = data['y_test']
        burst_threshold = float(data['burst_threshold'])
        
        print(f"數據載入: 訓練集 {X_train.shape}, 測試集 {X_test.shape}")
        print(f"爆量門檻: {burst_threshold:.2f}\n")
        
        # 創建 DataLoader
        train_dataset = CrowdFlowDataset(X_train, y_train)
        val_dataset = CrowdFlowDataset(X_test, y_test)
        
        train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
        
        # 創建模型變體
        input_dim = X_train.shape[1]
        variants = create_model_variants(input_dim)
        
        # 訓練每個變體
        for variant_name, variant_info in variants.items():
            print(f"\n{'-'*80}")
            print(f"訓練變體: {variant_info['name']}")
            print(f"描述: {variant_info['description']}")
            print(f"{'-'*80}")
            
            # 創建新模型實例
            model = variant_info['model'].to(device)
            
            # 損失函數
            criterion = WeightedMSELoss(threshold=burst_threshold, weight_burst=5.0)
            
            # 優化器
            optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
            
            # 學習率調度
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode='min', factor=0.5, patience=10
            )
            
            # 模型保存路徑
            model_save_path = f'resnet_models/grid{rank}_{variant_name}.pth'
            
            # 訓練
            start_time = time.time()
            history = train_model(
                model, train_loader, val_loader, criterion, optimizer, scheduler,
                device, max_epochs=200, patience=25, model_save_path=model_save_path
            )
            train_time = time.time() - start_time
            
            print(f"  ✓ 訓練完成！")
            print(f"    最佳驗證損失: {history['best_val_loss']:.4f}")
            print(f"    訓練時間: {train_time:.1f}秒 ({train_time/60:.1f}分鐘)")
            print(f"    模型已儲存: {model_save_path}")
            
            # 儲存訓練日誌
            log_data = {
                'grid_rank': rank,
                'grid_x': x,
                'grid_y': y,
                'variant_name': variant_name,
                'variant_description': variant_info['description'],
                'train_losses': [float(x) for x in history['train_losses']],
                'val_losses': [float(x) for x in history['val_losses']],
                'best_val_loss': float(history['best_val_loss']),
                'final_epoch': int(history['final_epoch']),
                'train_time_seconds': float(train_time),
                'burst_threshold': float(burst_threshold)
            }
            
            log_file = f'resnet_logs/grid{rank}_{variant_name}.json'
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
    
    print(f"\n{'='*80}")
    print("✅ 所有模型訓練完成！")
    print(f"{'='*80}\n")
    print("產生的檔案：")
    print("  模型: resnet_models/*.pth (15 個)")
    print("  日誌: resnet_logs/*.json (15 個)")

if __name__ == '__main__':
    main()
