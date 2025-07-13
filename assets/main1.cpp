#include <iostream>
#include <fstream>
#include "uper_encoder.h"
#include "CommonSafetyRequest.h"
#include "CommonSafetyRequest_converter.hpp"

using json = nlohmann::json;

int main(){
    // CommonSafetyRequest_t request = {};  // zero-initialize everything

    // // Allocate and assign timeStamp
    // request.timeStamp = new MinuteOfTheYear_t;
    // *(request.timeStamp) = 123456;

    // // Allocate and assign msgCnt
    // request.msgCnt = new MsgCount_t;
    // *(request.msgCnt) = 42;

    // // Skip id since it's optional and you don't want to set it
    // request.id = nullptr;

    // // Populate requests
    // RequestedItem_t itemA = RequestedItem_itemA;
    // RequestedItem_t itemC = RequestedItem_itemC;
    // RequestedItem_t itemI = RequestedItem_itemI;
    // RequestedItem_t itemN = RequestedItem_itemN;

    // // Allocate the array of RequestedItem_t pointers
    // request.requests.list.count = 4;
    // request.requests.list.size = 4;
    // request.requests.list.array = (RequestedItem_t**)calloc(4, sizeof(RequestedItem_t*));

    // // Allocate and assign each item
    // request.requests.list.array[0] = new RequestedItem_t(itemA);
    // request.requests.list.array[1] = new RequestedItem_t(itemC);
    // request.requests.list.array[2] = new RequestedItem_t(itemI);
    // request.requests.list.array[3] = new RequestedItem_t(itemN);

    // json j = to_JSON_CommonSafetyRequest(&request);
    // std::cout << "To JSON:\n" << j.dump(4) << "\n";

    // json j_new = {
    //     {"timeStamp", 123456},
    //     {"msgCnt", 42},
    //     {"requests", {"itemA", "itemC", "itemI", "itemN"}}
    // };

    std::ifstream inputFile("CommonSafetyRequest.json");
    if (!inputFile.is_open()) {
        std::cerr << "Failed to open CommonSafetyRequest.json\n";
        return 1;
    }

    json j;
    inputFile >> j;  // Parse JSON from file
    inputFile.close();

    std::cout << "Read JSON:\n" << j.dump(4) << "\n";


    CommonSafetyRequest_t parsed = to_STRUCT_CommonSafetyRequest(j);
    std::cout << "Parsed CommonSafetyRequest:\n";
    std::cout << "TimeStamp: " << (parsed.timeStamp ? *parsed.timeStamp : 0) << "\n";
    std::cout << "MsgCount: " << (parsed.msgCnt ? *parsed.msgCnt : 0) << "\n";
    std::cout << "Requests: ";
    for (int i = 0; i < parsed.requests.list.count; ++i) {
        std::cout << *(parsed.requests.list.array[i]) << " ";
    }
    std::cout << "\n";

    uint8_t encoded_buf[1024];
    asn_enc_rval_t encode_result = uper_encode_to_buffer(
        &asn_DEF_CommonSafetyRequest,
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

    CommonSafetyRequest_t *decoded_request = 0;
    asn_dec_rval_t dec_ret = uper_decode(
        0,
        &asn_DEF_CommonSafetyRequest,
        (void**)&decoded_request,
        encoded_buf,
        encoded_bytes,
        0, 0 // don't skip bits, complete input
    );

    if (dec_ret.code != RC_OK) {
        std::cerr << "Decoding failed.\n";
        return 1;
    }

    json j_back = to_JSON_CommonSafetyRequest(*decoded_request);
    std::cout << "Decoded back to JSON:\n" << j_back.dump(4) << "\n";

    test(&j,&j_back)

    return 0;
}