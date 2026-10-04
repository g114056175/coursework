"""
訓練網格2和網格3的所有模型變體

僅訓練這兩個網格，網格1已訓練完成
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
import os
import time
import sys

sys.path.insert(0, os.path.dirname(__file__))
from resnet_models_29 import create_model_variants

class CrowdFlowDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class WeightedMSELoss(nn.Module):
    def __init__(self, threshold, weight_burst=5.0):
        super(WeightedMSELoss, self).__init__()
        self.threshold = threshold
        self.weight_burst = weight_burst
    
    def forward(self, pred, target):
        weights = torch.where(
            target > self.threshold,
            torch.tensor(self.weight_burst),
            torch.tensor(1.0)
        ).to(pred.device)
        
        loss = weights * (pred - target) ** 2
        return loss.mean()

def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    
    for X_batch, y_batch in dataloader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device)
        
        optimizer.zero_grad()
        output = model(X_batch)
        loss = criterion(output, y_batch)
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item() * len(X_batch)
    
    return total_loss / len(dataloader.dataset)

def validate(model, dataloader, criterion, device):
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
    
    best_val_loss = float('inf')
    epochs_no_improve = 0
    train_losses = []
    val_losses = []
    
    for epoch in range(max_epochs):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss = validate(model, val_loader, criterion, device)
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        scheduler.step(val_loss)
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_no_improve = 0
            
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
        
        if (epoch + 1) % 10 == 0:
            print(f"    Epoch {epoch+1:3d}: Train={train_loss:.4f}, Val={val_loss:.4f}, "
                  f"Best={best_val_loss:.4f}")
        
        if epochs_no_improve >= patience:
            print(f"    早停於 epoch {epoch+1}")
            break
    
    return {
        'train_losses': train_losses,
        'val_losses': val_losses,
        'best_val_loss': best_val_loss,
        'final_epoch': epoch + 1
    }

def main():
    print("="*80)
    print("訓練網格2和網格3的ResNet模型")
    print("="*80)
    print()
    
    device = torch.device('cpu')
    
    grids = [
        {'rank': 2, 'x': 80, 'y': 93, 'feature': '第二高人流'},
        {'rank': 3, 'x': 79, 'y': 97, 'feature': '最大瞬間湧入'}
    ]
    
    for grid_info in grids:
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        
        print(f"{'='*80}")
        print(f"網格 #{rank}: ({x}, {y}) - {feature}")
        print(f"{'='*80}\n")
        
        data_file = f'resnet_features/grid_{rank}_{x}_{y}.npz'
        data = np.load(data_file, allow_pickle=True)
        
        X_train = data['X_train']
        X_test = data['X_test']
        y_train = data['y_train']
        y_test = data['y_test']
        burst_threshold = float(data['burst_threshold'])
        
        train_dataset = CrowdFlowDataset(X_train, y_train)
        val_dataset = CrowdFlowDataset(X_test, y_test)
        
        train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
        
        input_dim = X_train.shape[1]
        variants = create_model_variants(input_dim)
        
        variant_names = ['baseline', 'deep', 'wide', 'leaky_relu', 'gelu']
        
        for variant_name in variant_names:
            variant_info = variants[variant_name]
            
            print(f"\n{'-'*80}")
            print(f"{variant_info['name']}: {variant_info['description']}")
            print(f"{'-'*80}")
            
            model = variant_info['model'].to(device)
            criterion = WeightedMSELoss(threshold=burst_threshold, weight_burst=5.0)
            optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=10)
            
            model_save_path = f'resnet_models/grid{rank}_{variant_name}.pth'
            
            start_time = time.time()
            history = train_model(model, train_loader, val_loader, criterion, optimizer, scheduler,
                                device, max_epochs=200, patience=25, model_save_path=model_save_path)
            train_time = time.time() - start_time
            
            print(f"  ✓ 最佳驗證損失: {history['best_val_loss']:.4f}, 訓練時間: {train_time:.1f}秒")
            
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
    print("✅ 訓練完成！")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
