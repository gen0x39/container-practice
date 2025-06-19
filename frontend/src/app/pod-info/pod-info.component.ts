// frontend/src/app/pod-info/pod-info.component.ts
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-pod-info',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="pod-info-container">
      <button 
        class="pod-info-button" 
        (click)="loadPodInfo()"
        [disabled]="loading">
        {{ loading ? '情報取得中...' : 'Pod情報を表示' }}
      </button>
      
      <div *ngIf="podInfo" class="pod-info-display">
        <h3>フロントエンドPod情報</h3>
        <div class="info-grid">
          <div class="info-item">
            <strong>Pod名:</strong> {{ podInfo.pod_name }}
          </div>
          <div class="info-item">
            <strong>Pod IP:</strong> {{ podInfo.pod_ip }}
          </div>
          <div class="info-item">
            <strong>Node名:</strong> {{ podInfo.node_name }}
          </div>
          <div class="info-item">
            <strong>クライアントIP:</strong> {{ podInfo.client_ip }}
          </div>
          <div class="info-item">
            <strong>環境:</strong> {{ podInfo.environment }}
          </div>
        </div>
      </div>
      
      <div *ngIf="error" class="error-message">
        エラー: {{ error }}
      </div>
    </div>
  `,
  styles: [`
    .pod-info-container {
      margin: 20px 0;
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
      background: #f9f9f9;
    }
    
    .pod-info-button {
      background: #007bff;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      margin-bottom: 15px;
    }
    
    .pod-info-button:hover:not(:disabled) {
      background: #0056b3;
    }
    
    .pod-info-button:disabled {
      background: #6c757d;
      cursor: not-allowed;
    }
    
    .pod-info-display {
      background: white;
      padding: 15px;
      border-radius: 4px;
      border: 1px solid #e9ecef;
    }
    
    .pod-info-display h3 {
      margin-top: 0;
      color: #333;
      border-bottom: 2px solid #007bff;
      padding-bottom: 8px;
    }
    
    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 10px;
    }
    
    .info-item {
      padding: 8px 12px;
      background: #f8f9fa;
      border-radius: 4px;
      border-left: 3px solid #007bff;
    }
    
    .info-item strong {
      color: #495057;
    }
    
    .error-message {
      color: #dc3545;
      background: #f8d7da;
      padding: 10px;
      border-radius: 4px;
      border: 1px solid #f5c6cb;
      margin-top: 10px;
    }
  `]
})
export class PodInfoComponent implements OnInit {
  podInfo: any = null;
  loading = false;
  error: string | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    // コンポーネント初期化時に自動でPod情報を取得
    this.loadPodInfo();
  }

  loadPodInfo() {
    this.loading = true;
    this.error = null;

    this.http.get(`${environment.apiUrl}/frontend-info`, {
      observe: 'response'
    }).subscribe({
      next: (response: any) => {
        this.podInfo = response.body;
        
        // ヘッダー情報もコンソールに出力（デバッグ用）
        console.log('Response Headers:', response.headers);
        console.log('X-Pod-Name:', response.headers.get('X-Pod-Name'));
        console.log('X-Pod-IP:', response.headers.get('X-Pod-IP'));
        
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message || 'Pod情報の取得に失敗しました';
        this.loading = false;
        console.error('Pod情報取得エラー:', err);
      }
    });
  }
}
