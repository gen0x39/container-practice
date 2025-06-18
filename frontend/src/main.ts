// import { bootstrapApplication } from '@angular/platform-browser';
// import { appConfig } from './app/app.config';
import { App } from './app/app';
import { ItemsComponent } from './app/items/items.component';
import { Routes } from '@angular/router';
import { appConfig } from './app/app.config';
import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';

/*
bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
*/

/*
export const routes: Routes = [
  { path: '', component: App },
  { path: 'items', component: ItemsComponent }
];
*/


bootstrapApplication(App, {
  ...appConfig,
  providers: [
    ...(appConfig.providers || []),
    provideHttpClient()
  ]
});
