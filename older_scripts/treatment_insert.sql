use diagnosebot;

insert into treatment (`Immediate`,`SecondStep`, `ThirdStep`, `LongTerm`, `TreatmentLevel`, `DiseaseID`) 
	values ('Get bed rest', 'Take cold medicine, OTC', 'Drink plenty of fluids', 'Saline drops and sprays', 5, 1);
insert into treatment (`Immediate`,`SecondStep`, `ThirdStep`, `LongTerm`, `TreatmentLevel`, `DiseaseID`) 
	values ('Get bed rest', 'Take OTC cold medicine and antibiotics', 'Drink plenty of fluids', 'Saline drops and sprays', 4, 1);
insert into treatment (`Immediate`,`SecondStep`, `ThirdStep`, `LongTerm`, `TreatmentLevel`, `DiseaseID`) 
	values ('See your physician', 'Antibiotics or Antifungals', 'Rest', 'OTC fever reducers and cough medicines', 4, 2);
insert into treatment (`Immediate`,`SecondStep`, `ThirdStep`, `LongTerm`, `TreatmentLevel`, `DiseaseID`) 
	values ('Antibiotics or Antifungals', 'Rest', 'OTC fever reducers', 'OTC cough medicinces', 5, 2);
insert into treatment (`Immediate`,`SecondStep`, `ThirdStep`, `LongTerm`, `TreatmentLevel`, `DiseaseID`) 
	values ('See your physician', 'Prescription drugs', 'Physician Care', 'Supervised care', 4, 3);
insert into treatment (`Immediate`,`SecondStep`, `ThirdStep`, `LongTerm`, `TreatmentLevel`, `DiseaseID`) 
	values ('Call 911', 'Seek treatment immediately', 'Emergency services', 'Supervised care', 4, 4);
insert into treatment (`Immediate`,`SecondStep`, `ThirdStep`, `LongTerm`, `TreatmentLevel`, `DiseaseID`) 
	values ('See your physcian', 'Antibiotic treatments', 'Rest', 'Supervised care', 4, 5);