import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { ReportService } from '../../services/report.service';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, MatTabsModule, MatProgressBarModule],
  template: `
    <div style="padding: 20px;">
      <h2 class="mat-h2">Leave Reports (HR)</h2>
      <mat-card>
        <mat-tab-group>
          <!-- Utilization Report -->
          <mat-tab label="Utilization Report">
            <div style="padding: 20px;">
              <table mat-table [dataSource]="utilizationData" class="mat-elevation-z2" style="width: 100%;">
                <ng-container matColumnDef="leave_type">
                  <th mat-header-cell *matHeaderCellDef> Leave Type </th>
                  <td mat-cell *matCellDef="let element"> {{element.leave_type_name}} </td>
                </ng-container>
                <ng-container matColumnDef="allocated">
                  <th mat-header-cell *matHeaderCellDef> Total Allocated </th>
                  <td mat-cell *matCellDef="let element"> {{element.total_allocated}} </td>
                </ng-container>
                <ng-container matColumnDef="used">
                  <th mat-header-cell *matHeaderCellDef> Total Used </th>
                  <td mat-cell *matCellDef="let element"> {{element.total_used}} </td>
                </ng-container>
                <ng-container matColumnDef="utilization">
                  <th mat-header-cell *matHeaderCellDef> Utilization % </th>
                  <td mat-cell *matCellDef="let element"> 
                    {{element.utilization_percentage | number:'1.1-2'}}%
                    <mat-progress-bar mode="determinate" [value]="element.utilization_percentage"></mat-progress-bar>
                  </td>
                </ng-container>
                <tr mat-header-row *matHeaderRowDef="['leave_type', 'allocated', 'used', 'utilization']"></tr>
                <tr mat-row *matRowDef="let row; columns: ['leave_type', 'allocated', 'used', 'utilization'];"></tr>
              </table>
            </div>
          </mat-tab>

          <!-- Department Report -->
          <mat-tab label="Department Report">
            <div style="padding: 20px;">
              <table mat-table [dataSource]="departmentData" class="mat-elevation-z2" style="width: 100%;">
                <ng-container matColumnDef="department">
                  <th mat-header-cell *matHeaderCellDef> Department </th>
                  <td mat-cell *matCellDef="let element"> {{element.department}} </td>
                </ng-container>
                <ng-container matColumnDef="employees">
                  <th mat-header-cell *matHeaderCellDef> Headcount </th>
                  <td mat-cell *matCellDef="let element"> {{element.employee_count}} </td>
                </ng-container>
                <ng-container matColumnDef="leaves_taken">
                  <th mat-header-cell *matHeaderCellDef> Leaves Taken </th>
                  <td mat-cell *matCellDef="let element"> {{element.total_leaves_taken}} </td>
                </ng-container>
                <ng-container matColumnDef="pending">
                  <th mat-header-cell *matHeaderCellDef> Pending Requests </th>
                  <td mat-cell *matCellDef="let element"> {{element.pending_requests}} </td>
                </ng-container>
                <tr mat-header-row *matHeaderRowDef="['department', 'employees', 'leaves_taken', 'pending']"></tr>
                <tr mat-row *matRowDef="let row; columns: ['department', 'employees', 'leaves_taken', 'pending'];"></tr>
              </table>
            </div>
          </mat-tab>
        </mat-tab-group>
      </mat-card>
    </div>
  `
})
export class ReportsComponent implements OnInit {
  utilizationData: any[] = [];
  departmentData: any[] = [];

  constructor(private reportService: ReportService) {}

  ngOnInit() {
    this.reportService.getUtilizationReport().subscribe(data => this.utilizationData = data);
    this.reportService.getDepartmentReport().subscribe(data => this.departmentData = data);
  }
}

