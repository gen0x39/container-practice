// src/app/items/items.component.ts
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

interface Rating {
  count: number;
  rate: number;
}

interface Item {
  id: number;
  title: string;
  price: number;
  description: string;
  category: string;
  image: string;
  rating: Rating;
}

@Component({
  selector: 'app-items',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container">
      <h2>Itemsページ</h2>
      <ul class="items-list">
        <li *ngFor="let item of items" class="item-card">
          <div class="item-header">
            <h3 class="item-title">{{ item.title }}</h3>
            <span class="item-category">{{ item.category }}</span>
          </div>
          
          <div class="item-details">
            <div class="item-rating">
              <span class="stars">
                <span *ngFor="let star of [1,2,3,4,5]" 
                      class="star" 
                      [class.filled]="star <= item.rating.rate">
                  ★
                </span>
              </span>
              <span class="rating-text">{{ item.rating.rate }} ({{ item.rating.count }}件)</span>
            </div>
            
            <div class="item-price">
              <span class="price">¥{{ item.price | number:'1.0-0' }}</span>
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
    }
    
    .items-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    
    .item-card {
      background: white;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
    }
    
    .item-title {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 600;
      color: #333;
      flex: 1;
      margin-right: 12px;
    }
    
    .item-category {
      background: #e3f2fd;
      color: #1976d2;
      padding: 4px 8px;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 500;
      text-transform: capitalize;
      white-space: nowrap;
    }
    
    .item-details {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .item-rating {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .stars {
      display: flex;
      gap: 2px;
    }
    
    .star {
      color: #ddd;
      font-size: 1rem;
    }
    
    .star.filled {
      color: #ffc107;
    }
    
    .rating-text {
      font-size: 0.9rem;
      color: #666;
    }
    
    .item-price {
      text-align: right;
    }
    
    .price {
      font-size: 1.2rem;
      font-weight: 700;
      color: #2e7d32;
    }
    
    @media (max-width: 600px) {
      .item-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
      }
      
      .item-details {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
      }
      
      .item-price {
        text-align: left;
      }
    }
  `]
})

export class ItemsComponent implements OnInit {
  items: Item[] = [];
  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.http.get<Item[]>('http://localhost:8000/items')
      .subscribe(data => {
        this.items = data;
      });
  }
}
