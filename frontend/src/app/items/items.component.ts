// src/app/items/items.component.ts
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';

interface AsciiArt {
  id: number;
  title: string;
  content: string;
  category: string;
  author: string;
  likes: number;
}

@Component({
  selector: 'app-items',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container">
      <h2>🎨 ASCIIアートギャラリー</h2>
      <ul class="ascii-list">
        <li *ngFor="let art of asciiArts" class="ascii-card">
          <div class="ascii-header">
            <h3 class="ascii-title">{{ art.title }}</h3>
            <span class="ascii-category">{{ art.category }}</span>
          </div>
          
          <div class="ascii-content">
            <pre class="ascii-art">{{ art.content }}</pre>
          </div>
          
          <div class="ascii-footer">
            <div class="ascii-author">
              <span class="author">�� {{ art.author }}</span>
            </div>
            
            <div class="ascii-actions">
              <button class="like-btn" (click)="likeArt(art)">
                ❤️ {{ art.likes }}
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
  `,
  styles: [`
    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      font-family: 'Courier New', monospace;
    }
    
    .ascii-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    
    .ascii-card {
      background: white;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .ascii-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 15px;
    }
    
    .ascii-title {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 600;
      color: #333;
      flex: 1;
      margin-right: 12px;
    }
    
    .ascii-category {
      background: #e3f2fd;
      color: #1976d2;
      padding: 4px 8px;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 500;
      text-transform: capitalize;
      white-space: nowrap;
    }
    
    .ascii-content {
      margin: 15px 0;
      background: #f9f9f9;
      border-radius: 4px;
      padding: 15px;
      overflow-x: auto;
    }
    
    .ascii-art {
      margin: 0;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      line-height: 1.2;
      white-space: pre;
      color: #333;
    }
    
    .ascii-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 15px;
    }
    
    .ascii-author {
      font-size: 0.9rem;
      color: #666;
    }
    
    .ascii-actions {
      display: flex;
      gap: 10px;
    }
    
    .like-btn {
      background: none;
      border: 1px solid #ccc;
      padding: 8px 12px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.2s ease;
    }
    
    .like-btn:hover {
      background: #f0f0f0;
      border-color: #999;
    }
    
    @media (max-width: 600px) {
      .ascii-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
      }
      
      .ascii-footer {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
      }
      
      .ascii-art {
        font-size: 10px;
      }
    }
  `]
})
export class ItemsComponent implements OnInit {
  asciiArts: AsciiArt[] = [];

  constructor(private http: HttpClient) { }

  ngOnInit() {
    // chiikawa_01.txtファイルを読み込む
    this.loadAsciiArt();
  }

  private loadAsciiArt() {
    // 新しいasciiディレクトリからファイルを読み込み
    const apiUrl = environment.apiUrl
    
    // バックエンドの/ascii-allエンドポイントからすべてのASCIIアートを取得
    this.http.get<AsciiArt[]>(`${apiUrl}/ascii-all`)
      .subscribe({
        next: (arts: AsciiArt[]) => {
          console.log('ASCIIアート読み込み成功:', { 
            count: arts.length,
            arts: arts.map(art => ({ 
              id: art.id, 
              title: art.title,
              contentLength: art.content.length 
            })),
            timestamp: new Date().toISOString()
          });
          
          this.asciiArts = arts;
        },
        error: (error) => {
          console.error('ASCIIアート読み込みエラー:', {
            error: error,
            apiUrl: `${apiUrl}/ascii-all`,
            timestamp: new Date().toISOString()
          });
          
          // エラー時のフォールバック
          this.asciiArts = [{
            id: 1,
            title: 'ちいかわ（フォールバック）',
            content: `
  /\\_/\\
 ( o.o )
  > ^ <
            `,
            category: 'アニメ',
            author: 'システム',
            likes: 0
          }];
        }
      });
  }

  likeArt(art: AsciiArt) {
    art.likes++;
    console.log('いいね追加:', { artId: art.id, newLikes: art.likes });
  }
}
