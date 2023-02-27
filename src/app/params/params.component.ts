import { Component } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-params',
  templateUrl: './params.component.html',
  styleUrls: ['./params.component.css']
})

export class ParamsComponent {
  // constructor(private params: FormBuilder) {}
  
  paramsForm: FormGroup = new FormGroup({
    train_metadata: new FormControl(''),
    train_multimedia: new FormControl(''),
    test_metadata: new FormControl(''),
    test_multimedia: new FormControl(''),
    misc_url: new FormControl('')
  });

  submitFn(){
    console.log(this.paramsForm.value);
  }

}
