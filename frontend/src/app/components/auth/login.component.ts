import { Component, Optional } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  form: FormGroup;
  loading = false;
  error: string | null = null;

  constructor(
    private fb: FormBuilder,
    private auth: AuthService,
    private router: Router,
    @Optional() private dialogRef?: MatDialogRef<LoginComponent>
  ) {
    this.form = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  submit() {
    if (this.form.invalid) return;
    this.loading = true;
    this.error = null;
    const { username, password } = this.form.value;
    this.auth.login(username, password).subscribe(
      (res) => {
        this.auth.setSession(res.access_token, res.role);
        if (this.dialogRef) {
          this.dialogRef.close(true);
        }
        this.router.navigate(['/inicio']);
      },
      (err) => {
        this.error = 'Credenciales incorrectas';
        this.loading = false;
      }
    );
  }
}
