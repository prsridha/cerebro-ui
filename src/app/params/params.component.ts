import { Component } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-params',
  templateUrl: './params.component.html',
  styleUrls: ['./params.component.css']
})

export class ParamsComponent {
  constructor(private params: FormBuilder) {}
  
  paramsForm: FormGroup = new FormGroup({
    train_metadata: new FormControl(''),
    train_multimedia: new FormControl(''),
    test_metadata: new FormControl(''),
    test_multimedia: new FormControl('')
  });

  onSubmit(){
    alert("YAAAYYY");
    console.log(this.paramsForm.value);
  }

}
