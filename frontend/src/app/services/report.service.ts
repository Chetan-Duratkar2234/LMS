import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ReportService {
  private apiUrl = 'http://localhost:8000/api/v1/reports';

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders() {
    const user = this.authService.currentUserValue;
    return new HttpHeaders({
      'Authorization': `Bearer ${user?.token}`
    });
  }

  getUtilizationReport(year: number = 2026): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/utilization?year=${year}`, { headers: this.getHeaders() });
  }

  getDepartmentReport(year: number = 2026): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/department?year=${year}`, { headers: this.getHeaders() });
  }

  getMonthlyReport(year: number = 2026): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/monthly?year=${year}`, { headers: this.getHeaders() });
  }
}
