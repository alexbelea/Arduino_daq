  /*
  * Reads 4 analog inputs (0-5V) for recording_dur seconds
  * Streams data to PC while recording
  * 
  */
  // change to 1 to print debug messages on Serial Monitor
  bool debug = false;

  const int analogInputs[] = {A0, A1, A2, A3};
  
  
  // set up the global varialbes
  unsigned long start_time;
  const unsigned long recording_dur = 5000; // 25 seconds in milliseconds (ENSURE python code is greater than this)
  unsigned long last_sample_time = 0;
  const unsigned long min_samp_interval = 2; // Sample every 2ms (adjust for stability)
  bool recording = false;
  int sample_count = 0;
  
  void setup() {
    // serial communication at 115200 bps
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
        if(debug) Serial.println("received START command");

        // Clear any remaining data in serial buffer
        while (Serial.available()) {
          Serial.read();
        }
        
        // Reset sample counter
        sample_count = 0;
        
        // Send header once
        Serial.println("Sample,Time(ms),A0(V),A1(V),A2(V),A3(V)");
        
        // Start recording
        recording = true;
        start_time = millis();
        last_sample_time = start_time;
        
        // Send confirmation
        Serial.println("RECORDING_STARTED");
      }
    }
    
    // If we're recording, collect and send data immediately
    if (recording) {
      if(debug) Serial.println("Recording!");
      unsigned long currentTime = millis();
      unsigned long elapsed_time = currentTime - start_time;
      
      // Check if we're still within the recording period
      if (elapsed_time <= recording_dur) {
        if(debug) Serial.println("elapsed time << duration");
        // Only sample at the specified interval
        if (currentTime - last_sample_time >= min_samp_interval) {
          last_sample_time = currentTime;
          
          // Increment sample counter
          sample_count++;
          
          // Start building the output string
          String data_string = String(sample_count) + "," + String(elapsed_time);
          
          // Multiplex through the four inputs sequentially
          for (int i = 0; i < 4; i++) {
            if(debug) Serial.println("reading input: " + String(i));
            int raw_value = analogRead(analogInputs[i]);
            float voltage = raw_value * (5.0 / 1023.0);
            data_string += "," + String(voltage, 3);
          }
          
          // Send the complete data string at once
          Serial.println(data_string);
        }
      }
      else {
        // End of recording
        recording = false;
        
        // Send notification that recording is complete
        Serial.println("RECORDING_COMPLETE");
        Serial.print("SAMPLES_COLLECTED:");
        Serial.println(sample_count);
        Serial.println("END_OF_DATA");
      }
    }
  }
