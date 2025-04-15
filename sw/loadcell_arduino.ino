#include "HX711.h"

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;

HX711 scale;

void setup() {
  Serial.begin(9600);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  
  Serial.println("Initializing scale...");
  scale.set_scale();    // Default to 1 for raw data
  scale.tare();         // Reset the scale to 0

  Serial.println("Ready to read load cell values...");
}

void loop() {
  if (scale.is_ready()) {
    long reading = scale.get_units();  // or .read() for raw ADC value
    Serial.print("Reading: ");
    Serial.println(reading);
  } else {
    Serial.println("HX711 not found.");
  }
  
}
