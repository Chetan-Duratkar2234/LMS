import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, MatChipsModule, MatButtonModule, MatIconModule],
  providers: [DatePipe],
  template: `
    <div style="padding: 20px;">
      <h2 class="mat-h2">User Management</h2>
      <mat-card>
        <table mat-table [dataSource]="usersData" class="mat-elevation-z2" style="width: 100%;">
          <ng-container matColumnDef="employee_code">
            <th mat-header-cell *matHeaderCellDef> Employee Code </th>
            <td mat-cell *matCellDef="let element"> {{element.employee_code}} </td>
          </ng-container>
          <ng-container matColumnDef="name">
            <th mat-header-cell *matHeaderCellDef> Name </th>
            <td mat-cell *matCellDef="let element"> <b>{{element.name}}</b> </td>
          </ng-container>
          <ng-container matColumnDef="email">
            <th mat-header-cell *matHeaderCellDef> Email </th>
            <td mat-cell *matCellDef="let element"> {{element.email}} </td>
          </ng-container>
          <ng-container matColumnDef="role">
            <th mat-header-cell *matHeaderCellDef> Role </th>
            <td mat-cell *matCellDef="let element">
              <mat-chip>{{element.role}}</mat-chip>
            </td>
          </ng-container>
          <ng-container matColumnDef="department">
            <th mat-header-cell *matHeaderCellDef> Department </th>
            <td mat-cell *matCellDef="let element"> {{element.department}} </td>
          </ng-container>
          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef> Status </th>
            <td mat-cell *matCellDef="let element">
              <span [style.color]="element.status === 'ACTIVE' ? 'green' : 'red'">
                {{element.status}}
              </span>
            </td>
          </ng-container>
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef> Actions </th>
            <td mat-cell *matCellDef="let element">
              <button mat-icon-button color="warn" *ngIf="element.role !== 'ADMIN' && element.status === 'ACTIVE'" (click)="toggleStatus(element, 'INACTIVE')" title="Disable Account">
                <mat-icon>block</mat-icon>
              </button>
              <button mat-icon-button color="primary" *ngIf="element.role !== 'ADMIN' && element.status === 'INACTIVE'" (click)="toggleStatus(element, 'ACTIVE')" title="Enable Account">
                <mat-icon>check_circle</mat-icon>
              </button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="['employee_code', 'name', 'email', 'role', 'department', 'status', 'actions']"></tr>
          <tr mat-row *matRowDef="let row; columns: ['employee_code', 'name', 'email', 'role', 'department', 'status', 'actions'];"></tr>
        </table>
        
        <div *ngIf="usersData.length === 0" style="padding: 30px; text-align: center; color: #666;">
          No users found.
        </div>
      </mat-card>
    </div>
  `
})
export class UsersComponent implements OnInit {
  usersData: any[] = [];

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.userService.getUsers().subscribe(data => this.usersData = data);
  }

  toggleStatus(user: any, newStatus: string) {
    if (confirm(`Are you sure you want to ${newStatus === 'INACTIVE' ? 'disable' : 'enable'} ${user.name}'s account?`)) {
      this.userService.updateUserStatus(user.employee_id, newStatus).subscribe(() => {
        this.loadUsers();
      });
    }
  }
}

