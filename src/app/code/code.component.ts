import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormGroup, FormControl } from '@angular/forms';

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

  constructor(private http: HttpClient) { }

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
    const formData = new FormData();
    formData.append('file', this.fileForm.get('fileSource')!.value!);
    this.http.post('http://localhost:8001/upload.php', formData)
      .subscribe(res => {
        console.log(res);
        alert('Uploaded Successfully.');
      })
  }
}
