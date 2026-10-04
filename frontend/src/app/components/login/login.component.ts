import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule
  ],
  template: `
    <div class="login-container">
      <mat-card class="login-card mat-elevation-z8">
        <mat-card-header>
          <div mat-card-avatar class="header-image"><mat-icon color="primary" class="large-icon">admin_panel_settings</mat-icon></div>
          <mat-card-title class="primary-color">LMS Portal</mat-card-title>
          <mat-card-subtitle>Sign in to manage your leaves</mat-card-subtitle>
        </mat-card-header>

        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
          <mat-card-content>
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Email</mat-label>
              <input matInput formControlName="email" type="email" placeholder="Enter your email">
              <mat-icon matSuffix>email</mat-icon>
              <mat-error *ngIf="loginForm.controls['email'].hasError('required')">Email is required</mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Password</mat-label>
              <input matInput formControlName="password" [type]="hidePassword ? 'password' : 'text'" placeholder="Enter your password">
              <button type="button" mat-icon-button matSuffix (click)="hidePassword = !hidePassword" [attr.aria-label]="'Hide password'" [attr.aria-pressed]="hidePassword">
                <mat-icon>{{hidePassword ? 'visibility_off' : 'visibility'}}</mat-icon>
              </button>
              <mat-error *ngIf="loginForm.controls['password'].hasError('required')">Password is required</mat-error>
            </mat-form-field>
            
            <div *ngIf="error" class="error-message mat-body-2">
              {{ error }}
            </div>
          </mat-card-content>
          <mat-card-actions align="end">
            <button mat-raised-button color="primary" type="submit" [disabled]="loginForm.invalid || loading" class="login-btn">
              {{ loading ? 'Signing in...' : 'Sign In' }}
            </button>
          </mat-card-actions>
        </form>
      </mat-card>
    </div>
  `,
  styles: [`
    .login-container {
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%);
    }
    .login-card {
      width: 100%;
      max-width: 400px;
      padding: 20px;
      border-radius: 12px;
    }
    .full-width {
      width: 100%;
      margin-bottom: 10px;
    }
    .large-icon {
      transform: scale(1.5);
      margin-top: 5px;
    }
    .primary-color {
      color: #1976d2;
      font-size: 1.5rem;
      font-weight: 500;
    }
    .error-message {
      color: #f44336;
      margin-top: -10px;
      margin-bottom: 10px;
      text-align: center;
    }
    .login-btn {
      width: 100%;
      padding: 8px 0;
      font-size: 1.1rem;
    }
    mat-card-header {
      margin-bottom: 20px;
    }
  `]
})
export class LoginComponent {
  loginForm: FormGroup;
  hidePassword = true;
  loading = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });

    if (this.authService.currentUserValue) {
      this.router.navigate(['/dashboard']);
    }
  }

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.loading = true;
    this.error = '';
    
    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        const user = this.authService.currentUserValue;
        if (user && user.role === 'ADMIN') {
          this.router.navigate(['/audit-logs']);
        } else {
          this.router.navigate(['/dashboard']);
        }
      },
      error: (err) => {
        this.error = 'Invalid email or password';
        this.loading = false;
      }
    });
  }
}
