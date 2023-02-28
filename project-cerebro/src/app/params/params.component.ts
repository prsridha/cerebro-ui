import { Component } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { FormControl, FormGroup } from '@angular/forms';
import { MatSnackBar } from "@angular/material/snack-bar";
import{ GlobalConstants } from '../common/constants';

interface ParamsDict {
  train_metadata: string
  train_multimedia: string
  test_metadata: string
  test_multimedia: string
  misc_url: [string]
}

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type':  'application/json',
  })
}

@Component({
  selector: 'app-params',
  templateUrl: './params.component.html',
  styleUrls: ['./params.component.css']
})

export class ParamsComponent {
  params = <ParamsDict>{}
  baseURL = GlobalConstants.backendURL;
  constructor(
    private httpClient: HttpClient,
    private snackBar: MatSnackBar
    ){}
  
  paramsForm: FormGroup = new FormGroup({
    train_metadata: new FormControl(''),
    train_multimedia: new FormControl(''),
    test_metadata: new FormControl(''),
    test_multimedia: new FormControl(''),
    misc_url: new FormControl('')
  });

  submitFn(){
    this.params.train_metadata = this.paramsForm.value.train_metadata;
    this.params.train_multimedia = this.paramsForm.value.train_multimedia;
    this.params.test_metadata = this.paramsForm.value.test_metadata;
    this.params.test_multimedia = this.paramsForm.value.test_multimedia;
    this.params.misc_url = [this.paramsForm.value.misc_url];
    
    this.httpClient.post(this.baseURL + "/params", this.params, httpOptions).subscribe((data: any) => {
      if (data.status == 200)
      {
        this.snackBar.open('Sent parameters to server!', 'Dismiss', {
          duration: 3000
        });
      } else {
        this.snackBar.open('Error occured', 'Dismiss', {
          duration: 3000
        });
      }
    });
  }
}
