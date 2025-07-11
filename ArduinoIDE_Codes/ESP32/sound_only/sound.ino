
#include "BluetoothA2DPSink.h"
 
BluetoothA2DPSink a2dp_sink;
 
void setup() {
    i2s_pin_config_t my_pin_config = {
        .bck_io_num = 27, ////BCLK 
        .ws_io_num = 26,  ////LRC pin 
        .data_out_num = 25, ///Din pin
        .data_in_num = I2S_PIN_NO_CHANGE
    };
    a2dp_sink.set_pin_config(my_pin_config);
    a2dp_sink.start("MyMusic");
}
 
void loop() {
}