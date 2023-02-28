import { Component } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { FormControl, FormGroup } from '@angular/forms';
import { MatSnackBar } from "@angular/material/snack-bar";
import { environment } from '../../environments/environment';

interface ParamsDict {
  train: {
    metadata_url: string,
    multimedia_url: string
  }
  valid: {
    metadata_url: string,
    multimedia_url: string
  }
  test: {
    metadata_url: string,
    multimedia_url: string
  }
  miscellaneous: [string, string]
}

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type':  'application/json'
  })
}

@Component({
  selector: 'app-params',
  templateUrl: './params.component.html',
  styleUrls: ['./params.component.css']
})

export class ParamsComponent {
  params = <ParamsDict>{}
  baseURL = environment.backendURL;
  constructor(
    private httpClient: HttpClient,
    private snackBar: MatSnackBar
    ){}
  
  paramsForm: FormGroup = new FormGroup({
    train_metadata: new FormControl(''),
    train_multimedia: new FormControl(''),
    valid_metadata: new FormControl(''),
    valid_multimedia: new FormControl(''),
    test_metadata: new FormControl(''),
    test_multimedia: new FormControl(''),
    misc_url1: new FormControl(''),
    misc_url2: new FormControl('')
  });

  submitFn(){
    this.params.train = {
      metadata_url: this.paramsForm.value.train_metadata,
      multimedia_url: this.paramsForm.value.train_multimedia
    }
    this.params.valid = {
      metadata_url: this.paramsForm.value.valid_metadata,
      multimedia_url: this.paramsForm.value.valid_multimedia
    }
    this.params.test = {
      metadata_url: this.paramsForm.value.test_metadata,
      multimedia_url: this.paramsForm.value.test_multimedia
    }
    this.params.miscellaneous = [this.paramsForm.value.misc_url1, this.paramsForm.value.misc_url2];
    
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
