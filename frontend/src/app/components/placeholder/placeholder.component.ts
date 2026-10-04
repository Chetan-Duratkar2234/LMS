import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-placeholder',
  standalone: true,
  imports: [CommonModule, MatCardModule],
  template: `
    <div style="padding: 20px;">
      <mat-card>
        <mat-card-header>
          <mat-card-title>Feature Coming Soon</mat-card-title>
        </mat-card-header>
        <mat-card-content style="padding-top: 20px;">
          <p>This module is currently being built and will be available in the next release.</p>
        </mat-card-content>
      </mat-card>
    </div>
  `
})
export class PlaceholderComponent {}
