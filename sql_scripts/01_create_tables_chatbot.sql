use diagnosebot;

DROP TABLE IF EXISTS `disease_to_symptom`;
DROP TABLE IF EXISTS `disease`;
CREATE TABLE `disease` (
  `DiseaseID` int NOT NULL AUTO_INCREMENT,
  `DiseaseName` varchar(50) NOT NULL,
  `Description` text,
  PRIMARY KEY (`DiseaseID`)
);

DROP TABLE IF EXISTS `symptom`;
CREATE TABLE `symptom` (
  `SymptomID` int NOT NULL AUTO_INCREMENT,
  `SymptomName` varchar(50) NOT NULL,
  `SymDesc` text,
  PRIMARY KEY (`SymptomID`)
) ; 

DROP TABLE IF EXISTS `symptom_severity`;
CREATE TABLE `symptom_severity` (
  `SeverityID` int NOT NULL AUTO_INCREMENT,
  `SeverityLevel` varchar(10) NOT NULL,
  PRIMARY KEY (`SeverityID`)
);

# As this was dropped initially due to the dependency no drop needed
CREATE TABLE `disease_to_symptom` (
  `DiseaseID` int NOT NULL,
  `SymptomID` int NOT NULL,
  `SeverityID` int NOT NULL,
  KEY `DiseaseID_idx` (`DiseaseID`),
  KEY `SymptomID_idx` (`SymptomID`),
  KEY `SeverityID_idx` (`SeverityID`),
  CONSTRAINT `DiseaseID` FOREIGN KEY (`DiseaseID`) REFERENCES `disease` (`DiseaseId`),
  CONSTRAINT `SeverityID` FOREIGN KEY (`SeverityID`) REFERENCES `symptom_severity` (`SeverityID`),
  CONSTRAINT `SymptomID` FOREIGN KEY (`SymptomID`) REFERENCES `symptom` (`SymptomID`)
);

DROP TABLE IF EXISTS `treatment`;
CREATE TABLE `treatment` (
  `TreatmentID` int NOT NULL AUTO_INCREMENT,
  `Immediate` varchar(250) NOT NULL,
  `SecondStep` varchar(250) NOT NULL,
  `ThirdStep` varchar(250) NOT NULL,
  `LongTerm` varchar(250) NOT NULL,
  `DiseaseName` varchar(250) NOT NULL,
  PRIMARY KEY (`TreatmentID`)
);

DROP TABLE IF EXISTS `diagnosis`;
CREATE TABLE `diagnosis` (
  `DiagnosisID` int NOT NULL AUTO_INCREMENT,
  `Diagnosis` varchar(10) NOT NULL,
  `DiagnosisCount` int NOT NULL,
  `DiseaseID` int NOT NULL,
  `DiagnosisDate` DATE NOT NULL,
  PRIMARY KEY (`DiagnosisID`)
);
