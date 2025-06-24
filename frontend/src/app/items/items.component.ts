// src/app/items/items.component.ts
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';
import { LogService } from '../services/log.service';
import { FormsModule } from '@angular/forms';
import { EventEmitter, Output } from '@angular/core';

interface AsciiArt {
  id: number;
  title: string;
  content: string;
  category: string;
  author: string;
  likes: number;
  timestamp: string;
  tweet: string;
  like: number;
  rt: number;
}

interface Tweet {
  tweet: string;
  like: number;
  rt: number;
  id: string;
  title: string;
  category: string;
  author: string;
  timestamp: string;
  filename: string;
  content?: string;
  ascii?: string | null; // バックエンド修正に合わせて
}

interface TweetRequest {
  content: string;
  author: string;
  category: string;
  ascii_content: string;
}

@Component({
  selector: 'app-items',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
  <div class="twitter-container">
    <div class="header">
      <h1>🐦 ASCII Twitter</h1>
      <p>ASCIIアートでつぶやこう！</p>
    </div>
    <div class="main-content">
      <!-- 投稿フォーム -->
      <div class="post-form">
        <div class="post-header">
          <div class="user-avatar">👤</div>
          <div class="post-input-container">
            <textarea 
              class="post-textarea" 
              placeholder="ASCIIアートでつぶやいてみよう..."
              [(ngModel)]="newPost"
              maxlength="280"
            ></textarea>
            <div class="post-footer">
              <span class="char-count" [class.char-limit]="newPost.length > 260">
                {{ newPost.length }}/280
              </span>
              <input type="file" accept="image/*" (change)="onFileSelected($event)" #fileInput hidden />
              <button type="button" (click)="fileInput.click()">画像を選択</button>
              <span *ngIf="selectedImage" class="preview-label">プレビュー:</span>
              <img *ngIf="selectedImage" [src]="selectedImage" class="image-preview" />
              <button *ngIf="selectedImage" type="button" (click)="removeImage()">画像を削除</button>
              <button 
                class="post-btn" 
                [disabled]="!newPost.trim() && !imageFile || newPost.length > 280 || isPosting"
                (click)="submitPost()"
              >
                {{ isPosting ? '投稿中...' : '🐦 ツイート' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <!-- タイムライン -->
      <div class="timeline">
        <h2>ツイート</h2>
        <div *ngIf="isLoading" class="loading">読み込み中...</div>
        <div *ngFor="let tweet of tweets" class="tweet">
          <div class="tweet-header">
            <div class="user-info">
              <div class="user-avatar">👤</div>
              <div class="user-details">
                <span class="username">{{ tweet.author }}</span>
                <span class="timestamp">· {{ tweet.timestamp | date:'short' }}</span>
              </div>
            </div>
            <span class="category">{{ tweet.category }}</span>
          </div>
          <div class="tweet-content">
            <h3 class="tweet-title">{{ tweet.title }}</h3>
            <pre class="ascii-art" *ngIf="tweet.tweet && tweet.tweet !== tweet.content">{{ tweet.tweet }}</pre>
            <pre class="ascii-art" *ngIf="tweet.content">{{ tweet.content }}</pre>
          </div>
          <div class="tweet-actions">
            <button class="action-btn like-btn" (click)="likeTweet(tweet)">
              <span class="action-icon" [class.liked]="tweet.like > 0">❤️</span>
              <span class="action-count">{{ tweet.like }}</span>
            </button>
            <button class="action-btn retweet-btn" (click)="retweetTweet(tweet)">
              <span class="action-icon">🔄</span>
              <span class="action-count">{{ tweet.rt }}</span>
            </button>
            <button class="action-btn reply-btn">
              <span class="action-icon">💬</span>
              <span class="action-count">0</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  `,
  styles: [`
    .twitter-container {
      background: #e6ecf0;
      min-height: 100vh;
      font-family: 'Segoe UI', 'Arial', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .header {
      width: 100%;
      background: #1da1f2;
      color: white;
      padding: 32px 0 16px 0;
      text-align: center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
      margin-bottom: 16px;
    }
    .header h1 {
      margin: 0;
      font-size: 2.2rem;
      font-weight: bold;
      letter-spacing: 2px;
    }
    .header p {
      margin: 8px 0 0 0;
      font-size: 1.1rem;
      opacity: 0.9;
    }
    .main-content {
      width: 100%;
      max-width: 900px;
      margin: 0 auto;
    }
    .post-form {
      display: flex;
      flex-direction: column;
      margin-bottom: 24px;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
      padding: 16px;
    }
    .post-textarea {
      width: 100%;
      min-height: 80px;
      font-family: 'Courier New', monospace;
      font-size: 1rem;
      margin-bottom: 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
      padding: 8px;
      resize: vertical;
    }
    .post-btn {
      align-self: flex-end;
      background: #1da1f2;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 8px 20px;
      font-size: 1rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    .post-btn:hover {
      background: #0d8ddb;
    }
    .timeline {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .tweet {
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
      padding: 16px;
      display: flex;
      flex-direction: column;
    }
    .tweet-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .user-info {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .username {
      font-weight: bold;
      color: #1da1f2;
    }
    .timestamp {
      color: #888;
      font-size: 0.9rem;
    }
    .category {
      background: #e6ecf0;
      color: #1da1f2;
      border-radius: 12px;
      padding: 2px 10px;
      font-size: 0.85rem;
      font-weight: bold;
    }
    .tweet-content {
      margin-bottom: 8px;
    }
    .ascii-art {
      font-family: 'Courier New', monospace;
      font-size: 1.1rem;
      white-space: pre;
      background: #f7f7f7;
      border-radius: 4px;
      padding: 8px;
      overflow-x: auto;
    }
    .tweet-actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
    .like-btn {
      background: none;
      border: none;
      color: #e0245e;
      font-size: 1.1rem;
      cursor: pointer;
      transition: color 0.2s;
    }
    .like-btn:hover {
      color: #ad1457;
    }
  `]
})

export class ItemsComponent implements OnInit {
  tweets: Tweet[] = [];
  newPost: string = '';
  isPosting: boolean = false;
  isLoading: boolean = false;

  selectedImage: string | ArrayBuffer | null = null;
  imageFile: File | null = null;

  constructor(
    private http: HttpClient,
    private logService: LogService
  ) { }

  ngOnInit() {
    this.loadAllTweets();
  }

  private loadAllTweets() {
    this.isLoading = true;
    this.http.get<Tweet[]>(`${environment.apiUrl}/tweets`)
      .subscribe({
        next: (data) => {
          this.tweets = data;
          this.logService.log('ツイートを読み込みました', String(data.length));
        },
        error: (error) => {
          console.error('ツイートの読み込みに失敗しました:', error);
          this.logService.log('ツイートの読み込みに失敗しました', error);
        },
        complete: () => {
          this.isLoading = false;
        }
      });
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.imageFile = input.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.selectedImage = e.target?.result || null;
      };
      reader.readAsDataURL(this.imageFile);
    }
  }

  removeImage() {
    this.selectedImage = null;
    this.imageFile = null;
  }

  submitPost() {
    if ((!this.newPost.trim() && !this.imageFile) || this.isPosting) return;
    this.isPosting = true;

    if (this.imageFile) {
      const formData = new FormData();
      formData.append('file', this.imageFile);
      formData.append('author', 'ユーザー');
      formData.append('category', '画像変換');

      this.http.post<any>(`${environment.apiUrl}/upload-image`, formData)
        .subscribe({
          next: (res) => {
            const tweetData: TweetRequest = {
              content: this.newPost,
              author: 'ユーザー',
              category: '画像＋テキスト',
              ascii_content: res.ascii_content // バックエンドのレスポンスに合わせて
            };
            this.http.post<Tweet>(`${environment.apiUrl}/tweet`, tweetData)
              .subscribe({
                next: (tweetRes) => {
                  this.tweets.unshift(tweetRes);
                  this.newPost = '';
                  this.removeImage();
                  this.isPosting = false;
                },
                error: (error) => {
                  alert('ツイートの投稿に失敗しました');
                  this.isPosting = false;
                }
              });
          },
          error: (error) => {
            alert('画像のアップロードまたは変換に失敗しました');
            this.isPosting = false;
          }
        });
    } else {
      const tweetData: TweetRequest = {
        content: this.newPost,
        author: 'ユーザー',
        category: 'ユーザー投稿',
        ascii_content: ''
      };
      this.http.post<Tweet>(`${environment.apiUrl}/tweet`, tweetData)
        .subscribe({
          next: (response) => {
            this.tweets.unshift(response);
            this.newPost = '';
            this.isPosting = false;
          },
          error: (error) => {
            alert('ツイートの投稿に失敗しました');
            this.isPosting = false;
          }
        });
    }
  }

  likeTweet(tweet: Tweet) {
    tweet.like++;
  }

  retweetTweet(tweet: Tweet) {
    tweet.rt++;
  }
}
