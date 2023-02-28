import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormGroup, FormControl } from '@angular/forms';
import { MatSnackBar } from "@angular/material/snack-bar";

@Component({
  selector: 'app-code',
  templateUrl: './code.component.html',
  styleUrls: ['./code.component.css']
})
export class CodeComponent {
  fileForm = new FormGroup({
    file: new FormControl(''),
    fileSource: new FormControl('')
  });

  constructor(
    private httpClient: HttpClient,
    private snackBar: MatSnackBar
  ) { }

  onFileChange(event:any) {
    if (event.target.files.length > 0) {
      const file = event.target.files[0];
      this.fileForm.patchValue({
        fileSource: file
      });
    }
  }

  get f(){
    return this.fileForm.controls;
  }

  submit(){
    const url = "http://localhost:8080"
    const formData = new FormData();
    formData.append('file', this.fileForm.get('fileSource')!.value!);
    this.httpClient.post(url + "/save-code", formData).subscribe((data:any) => {
        if (data.status == 200)
        {
          this.snackBar.open('Uploaded code files to server!', 'Dismiss', {
            duration: 3000
          });
        } else {
          this.snackBar.open('Error occured', 'Dismiss', {
            duration: 3000
          });
        }
      })
  }
}
