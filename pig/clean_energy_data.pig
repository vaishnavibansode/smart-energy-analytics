raw_data = LOAD 'hdfs://localhost:9000/user/vaishnavi/smart-energy/raw/household_power_consumption.txt'
USING PigStorage(';')
AS (
    reading_date:chararray,
    reading_time:chararray,
    global_active_power:chararray,
    global_reactive_power:chararray,
    voltage:chararray,
    global_intensity:chararray,
    sub_metering_1:chararray,
    sub_metering_2:chararray,
    sub_metering_3:chararray
);

valid_data = FILTER raw_data BY
    reading_date != 'Date'
    AND global_active_power IS NOT NULL AND global_active_power != '?'
    AND global_reactive_power IS NOT NULL AND global_reactive_power != '?'
    AND voltage IS NOT NULL AND voltage != '?'
    AND global_intensity IS NOT NULL AND global_intensity != '?'
    AND sub_metering_1 IS NOT NULL AND sub_metering_1 != '?'
    AND sub_metering_2 IS NOT NULL AND sub_metering_2 != '?'
    AND sub_metering_3 IS NOT NULL AND sub_metering_3 != '?';

cleaned_data = FOREACH valid_data GENERATE
    reading_date AS reading_date,
    reading_time AS reading_time,
    SUBSTRING(reading_time, 0, 2) AS hour,
    (double)global_active_power AS global_active_power,
    (double)global_reactive_power AS global_reactive_power,
    (double)voltage AS voltage,
    (double)global_intensity AS global_intensity,
    (double)sub_metering_1 AS sub_metering_1,
    (double)sub_metering_2 AS sub_metering_2,
    (double)sub_metering_3 AS sub_metering_3;

STORE cleaned_data
INTO 'hdfs://localhost:9000/user/vaishnavi/smart-energy/processed/cleaned_energy'
USING PigStorage('\t');
