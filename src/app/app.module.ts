import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ToolbarComponent } from './toolbar/toolbar.component';
import { ParamsComponent } from './params/params.component';
import { CodeComponent } from './code/code.component';
import { LandingComponent } from './landing/landing.component';

@NgModule({
  declarations: [
    AppComponent,
    ToolbarComponent,
    ParamsComponent,
    CodeComponent,
    LandingComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FormsModule,
    ReactiveFormsModule,
    MatSlideToggleModule,
    MatToolbarModule,
    MatButtonModule,
    MatInputModule,
    MatSelectModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
