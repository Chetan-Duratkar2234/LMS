import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { LeaveService } from '../../services/leave.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-leave-request',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatButtonModule,
    MatSnackBarModule
  ],
  template: `
    <div class="form-container">
      <mat-card class="mat-elevation-z4 form-card">
        <mat-card-header>
          <mat-card-title>Apply for Leave</mat-card-title>
          <mat-card-subtitle>Fill out the form below to request time off</mat-card-subtitle>
        </mat-card-header>

        <form [formGroup]="leaveForm" (ngSubmit)="onSubmit()">
          <mat-card-content class="form-content">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Leave Type</mat-label>
              <mat-select formControlName="leave_type_id">
                <mat-option *ngFor="let type of leaveTypes" [value]="type.leave_type_id">
                  {{ type.leave_name }} ({{ type.leave_code }})
                </mat-option>
              </mat-select>
              <mat-error *ngIf="leaveForm.controls['leave_type_id'].hasError('required')">Leave type is required</mat-error>
            </mat-form-field>

            <div class="date-row">
              <mat-form-field appearance="outline" class="half-width">
                <mat-label>Start Date</mat-label>
                <input matInput [matDatepicker]="startPicker" formControlName="start_date" [min]="minDate">
                <mat-datepicker-toggle matIconSuffix [for]="startPicker"></mat-datepicker-toggle>
                <mat-datepicker #startPicker></mat-datepicker>
                <mat-error *ngIf="leaveForm.controls['start_date'].hasError('required')">Start date is required</mat-error>
              </mat-form-field>

              <mat-form-field appearance="outline" class="half-width">
                <mat-label>End Date</mat-label>
                <input matInput [matDatepicker]="endPicker" formControlName="end_date" [min]="leaveForm.get('start_date')?.value || minDate">
                <mat-datepicker-toggle matIconSuffix [for]="endPicker"></mat-datepicker-toggle>
                <mat-datepicker #endPicker></mat-datepicker>
                <mat-error *ngIf="leaveForm.controls['end_date'].hasError('required')">End date is required</mat-error>
              </mat-form-field>
            </div>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Reason</mat-label>
              <textarea matInput formControlName="reason" rows="4" placeholder="Briefly describe your reason for taking leave"></textarea>
              <mat-error *ngIf="leaveForm.controls['reason'].hasError('required')">Reason is required</mat-error>
            </mat-form-field>
          </mat-card-content>

          <mat-card-actions align="end">
            <button mat-button type="button" (click)="leaveForm.reset()">Clear</button>
            <button mat-raised-button color="primary" type="submit" [disabled]="leaveForm.invalid || loading">
              {{ loading ? 'Submitting...' : 'Submit Request' }}
            </button>
          </mat-card-actions>
        </form>
      </mat-card>
    </div>
  `,
  styles: [`
    .form-container {
      display: flex;
      justify-content: center;
      padding-top: 20px;
    }
    .form-card {
      width: 100%;
      max-width: 600px;
      padding: 10px;
    }
    .form-content {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 20px;
    }
    .full-width {
      width: 100%;
    }
    .date-row {
      display: flex;
      gap: 16px;
    }
    .half-width {
      flex: 1;
    }
    @media (max-width: 600px) {
      .date-row {
        flex-direction: column;
        gap: 0;
      }
    }
  `]
})
export class LeaveRequestComponent implements OnInit {
  leaveForm: FormGroup;
  leaveTypes: any[] = [];
  loading = false;
  minDate = new Date();

  constructor(
    private fb: FormBuilder,
    private leaveService: LeaveService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {
    this.leaveForm = this.fb.group({
      leave_type_id: ['', Validators.required],
      start_date: ['', Validators.required],
      end_date: ['', Validators.required],
      reason: ['', Validators.required]
    });
  }

  ngOnInit() {
    this.leaveService.getLeaveTypes().subscribe({
      next: (types) => this.leaveTypes = types,
      error: (err) => console.error('Failed to load leave types', err)
    });
  }

  onSubmit() {
    if (this.leaveForm.invalid) return;

    this.loading = true;
    const formValue = this.leaveForm.value;
    
    // Format dates to YYYY-MM-DD for backend
    const payload = {
      ...formValue,
      start_date: this.formatDate(formValue.start_date),
      end_date: this.formatDate(formValue.end_date)
    };

    this.leaveService.applyLeave(payload).subscribe({
      next: (res) => {
        this.snackBar.open('Leave request submitted successfully!', 'Close', { duration: 3000 });
        this.router.navigate(['/leave-list']);
      },
      error: (err) => {
        this.snackBar.open('Failed to submit leave request.', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  private formatDate(date: Date): string {
    const d = new Date(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    const year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
  }
}
