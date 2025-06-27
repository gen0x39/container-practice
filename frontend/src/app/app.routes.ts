import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component'; // 追加
import { ItemsComponent } from './items/items.component';
import { HealthComponent } from './health/health.component';

export const routes: Routes = [
  { path: '', component: ItemsComponent }, // ← ここをItemsComponentに
  { path: 'items', component: ItemsComponent },
  { path: 'health', component: HealthComponent }
];

