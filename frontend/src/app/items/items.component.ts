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
      <ul>
        <li *ngFor="let item of items">
          <h3>{{ item.title }}</h3>
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
  `]
})

export class ItemsComponent implements OnInit {
  items: Item[] = [];

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.http.get<Item[]>('http://localhost:8000/items')
      .subscribe(data => {
        this.items = data;
        console.log('取得したアイテム:', this.items);
      });
  }
}
