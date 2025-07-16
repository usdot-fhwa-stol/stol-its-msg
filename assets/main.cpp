// main.cpp
#include <iostream>
#include "AccelerationSet4Way.h"
#include "AccelerationSet4Way_converter.hpp"
#include "uper_encoder.h"

int main() {
    AccelerationSet4Way_t acc;
    acc.Long = 120;
    acc.lat = -85;
    acc.vert = 10;
    acc.yaw = 500;

    nlohmann::json j = to_JSON_AccelerationSet4Way(&acc);
    std::cout << "To JSON:\n" << j.dump(4) << "\n";

    AccelerationSet4Way_t parsed = to_STRUCT_AccelerationSet4Way(j);
    std::cout << "\nBack to struct:\n";
    std::cout << "long: " << parsed.Long << "\n";
    std::cout << "lat: " << parsed.lat << "\n";
    std::cout << "vert: " << parsed.vert << "\n";
    std::cout << "yaw: " << parsed.yaw << "\n";

    uint8_t encoded_buf[1024];
    asn_enc_rval_t encode_result = uper_encode_to_buffer(
        &asn_DEF_AccelerationSet4Way,
        nullptr, // constraints
        &acc,
        encoded_buf,
        sizeof(encoded_buf)
    );

    std::cout << "Encoded buffer (hex): ";
    for (size_t i = 0; i < (encode_result.encoded + 7) / 8; ++i) {
        printf("%02X ", encoded_buf[i]);
    }
    std::cout << "\n";

    if (encode_result.encoded == -1) {
        std::cerr << "Encoding failed.\n";
        return 1;
    }
    size_t encoded_bytes = (encode_result.encoded + 7) / 8;

    AccelerationSet4Way_t *decoded_acc=0;
    asn_dec_rval_t dec_ret = uper_decode(
        0,
        &asn_DEF_AccelerationSet4Way,
        (void**)&decoded_acc,
        encoded_buf,
        encoded_bytes,
        0, 0 // don't skip bits, complete input
    );

    if (dec_ret.code != RC_OK) {
        std::cerr << "Decoding failed.\n";
        return 1;
    }

    // Print to confirm
    nlohmann::json j_back = to_JSON_AccelerationSet4Way(decoded_acc);
    std::cout << "Decoded JSON:\n" << j_back.dump(4) << "\n";

    return 0;
}
