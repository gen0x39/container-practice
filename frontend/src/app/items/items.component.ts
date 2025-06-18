// src/app/items/items.component.ts
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-items',
  standalone: true,
  template: `<h2>Itemsページ</h2>`
})

export class ItemsComponent implements OnInit {
  items: any[] = [];

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.http.get<any[]>('http://localhost:8000/items')
      .subscribe(data => {
        this.items = data;
      });
  }
}
