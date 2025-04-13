  /*
  * Reads 4 analog inputs (0-5V) for recordingDuration seconds
  * Streams data to PC while recording
  * 
  */

  const int analogInputs[] = {A0, A1, A2, A3};
  
  
  // setup variables
  unsigned long startTime;
  const unsigned long recordingDuration = 5000; // 25 seconds in milliseconds (ENSURE python code is greater than this)
  unsigned long lastSampleTime = 0;
  const unsigned long minSampleInterval = 2; // Sample every 2ms (adjust for stability)
  bool isRecording = false;
  int sampleCount = 0;
  
  void setup() {
    // serial communication at standard 115200 bps
    Serial.begin(115200);
    
    // Set pins as input
    for (int i = 0; i < 4; i++) {
      pinMode(analogInputs[i], INPUT);
    }
    
    // Optimize ADC for faster sampling
    // Set ADC prescaler to 16 (default is 128)
    //
    // Bit: 7:enable; 6: initiate a convertion 5:
    //
    //
    //
    ADCSRA = (ADCSRA & 0xF8) | 0x04;
    
    // Wait for serial connection to establish
    delay(1000);
    
    // Send ready message
    Serial.println("ARDUINO_DAQ_READY");
  }
  
  void loop() {
    // Check if we received a command
    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      command.trim();
      
      if (command == "START") {
        // Clear any remaining data in serial buffer
        while (Serial.available()) {
          Serial.read();
        }
        
        // Reset sample counter
        sampleCount = 0;
        
        // Send header once
        Serial.println("Sample,Time(ms),A0(V),A1(V),A2(V),A3(V)");
        
        // Start recording
        isRecording = true;
        startTime = millis();
        lastSampleTime = startTime;
        
        // Send confirmation
        Serial.println("RECORDING_STARTED");
      }
    }
    
    // If we're recording, collect and send data immediately
    if (isRecording) {
      unsigned long currentTime = millis();
      unsigned long elapsedTime = currentTime - startTime;
      
      // Check if we're still within the recording period
      if (elapsedTime <= recordingDuration) {
        // Only sample at the specified interval
        if (currentTime - lastSampleTime >= minSampleInterval) {
          lastSampleTime = currentTime;
          
          // Increment sample counter
          sampleCount++;
          
          // Start building the output string
          String dataString = String(sampleCount) + "," + String(elapsedTime);
          
          // Multiplex through the four inputs sequentially
          for (int i = 0; i < 4; i++) {
            int rawValue = analogRead(analogInputs[i]);
            float voltage = rawValue * (5.0 / 1023.0);
            dataString += "," + String(voltage, 3);
          }
          
          // Send the complete data string at once
          Serial.println(dataString);
        }
      }
      else {
        // End of recording
        isRecording = false;
        
        // Send notification that recording is complete
        Serial.println("RECORDING_COMPLETE");
        Serial.print("SAMPLES_COLLECTED:");
        Serial.println(sampleCount);
        Serial.println("END_OF_DATA");
      }
    }
  }
