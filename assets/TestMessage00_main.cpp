#include <iostream>
#include <fstream>
#include "uper_encoder.h"
#include "TestMessage00.h"
#include "TestMessage00_converter.hpp"

using json = nlohmann::json;

int main(){

    std::ifstream inputFile("TestMessage00.json");
    if (!inputFile.is_open()) {
        std::cerr << "Failed to open CommonSafetyRequest.json\n";
        return 1;
    }
    json j;
    inputFile >> j;  // Parse JSON from file
    inputFile.close();

    std::cout << "Read JSON:\n" << j.dump(4) << "\n";

    TestMessage00_t parsed = to_STRUCT_TestMessage00(j);
    
    uint8_t encoded_buf[1024];
    asn_enc_rval_t encode_result = uper_encode_to_buffer(
        &asn_DEF_TestMessage00,
        nullptr, // constraints
        &parsed,
        encoded_buf,
        sizeof(encoded_buf)
    );

    if (encode_result.encoded == -1) {
        std::cerr << "Encoding failed.\n";
        return 1;
    }

    std::cout << "Encoded buffer (hex): ";
    for (size_t i = 0; i < (encode_result.encoded + 7) / 8; ++i) {
        printf("%02X ", encoded_buf[i]);
    }
    std::cout << "\n";

    size_t encoded_bytes = (encode_result.encoded + 7) / 8;
    
    TestMessage00_t *decoded=0;
    asn_dec_rval_t rval = uper_decode(
        0,
        &asn_DEF_TestMessage00,
        (void **)&decoded,
        encoded_buf,
        encoded_bytes,
        0, 0
    );

    if (rval.code != RC_OK) {
        std::cerr << "Decoding failed.\n";
        return 1;
    }

    // Successfully decoded
    std::cout << "Decoded successfully:\n" << to_JSON_TestMessage00(*decoded).dump(4) << "\n";

    return 0;  // Placeholder for main function
}