FUNCTION filter_and_save_data(filename)
    // Load data from CSV file into a table structure
    data_table = READ_CSV(filename)
    
    // Clean the data by converting text to numbers
    FOR EACH column IN data_table
        CONVERT column values to numeric type
        IF conversion fails for any value
            REPLACE with NaN (Not a Number)
    END FOR
    
    // Remove any rows containing NaN values
    REMOVE all rows with NaN values from data_table
    
    // Calculate sampling frequency
    time_differences = CALCULATE differences between consecutive time values
    typical_time_difference = FIND median of time_differences
    sampling_frequency = 1000.0 / typical_time_difference  // Convert ms to Hz
    
    // Process each data channel
    channel_list = ["A0(V)", "A1(V)", "A2(V)", "A3(V)"]
    
    FOR EACH channel_name IN channel_list
        IF channel_name EXISTS in data_table
            filtered_values = APPLY_LOWPASS_FILTER(original_values, sampling_frequency)
            ADD new column named channel_name + "_filtered" with filtered_values
        END IF
    END FOR
    
    // Save results to new file
    new_filename = REMOVE_EXTENSION(filename) + "_filtered.csv"
    WRITE data_table TO new_filename
    
    RETURN new_filename
END FUNCTION