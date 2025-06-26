import asn1tools

# Structured message (as a Python dict)

messages = {
   
"BasicSafetyMessage" : {
    1: {
    "messageId": 20,
    "value": {
        "coreData": {
            "msgCnt": 25,
            "id": b'\xF0\x3A\xD6\x10',
            "secMark": 38283,
            "lat": 389557079,
            "long": -771505975,
            "elev": 370,
            "accuracy": {
                "semiMajor": 255,
                "semiMinor": 255,
                "orientation": 65535
            },
            "transmission": "park",
            "speed": 0,
            "heading": 10201,
            "angle": -27,
            "accelSet": {
                "long": 0,
                "lat": 0,
                "vert": -127,
                "yaw": 0
            },
            "brakes": {
                "wheelBrakes": (b'\x10', 5),
                "traction": "unavailable",
                "abs": "unavailable",
                "scs": "unavailable",
                "brakeBoost": "unavailable",
                "auxBrakes": "unavailable"
            },
            "size": {
                "width": 200,
                "length": 500
            }
        }
        
    }
},

2:{
  
  
    "messageId": 20,
    "value": {
      "coreData": {
        "msgCnt": 58,
        "id": b'\xF0\x3A\xD6\x10',
        "secMark": 34521,
        "lat": 411234567,
        "long": -877654321,
        "elev": 250,
        "accuracy": {
          "semiMajor": 90,
          "semiMinor": 70,
          "orientation": 12000
        },
        "transmission": "forwardGears",
        "speed": 2250,
        "heading": 18000,
        "angle": -5,
        "accelSet": {
          "long": 10,
          "lat": -2,
          "vert": 5,
          "yaw": 15
        },
        "brakes": {
         "wheelBrakes": (b'\x10', 5),
          "traction": "on",
          "abs": "on",
          "scs": "on",
          "brakeBoost": "off",
          "auxBrakes": "off"
        },
        "size": {
          "width": 220,
          "length": 480
        }
      },
      "partII": [
        {
          "partII-Id": 0,
          "partII-Value": {
            "vehicleSafetyExt": {
              "events": [
                "eventHardBraking"
              ],
              "pathPrediction": {
                "radiusOfCurve": 32767,
                "confidence": 150
              },
              "lights": [
                "lowBeamHeadlightsOn",
                "daytimeRunningLightsOn"
              ]
            }
          }
        },
        {
          "partII-Id": 2,
          "partII-Value": {
            "supplementalVehicleExt": {
              "classification": 1,
              "classDetails": {
                "keyType": 1,
                "role": "basicVehicle",
                "hpmsType": "car"
              },
              "vehicleData": {
                "height": 180,
                "bumpers": {
                  "front": 70,
                  "rear": 72
                },
                "mass": 180,
                "trailerWeight": 0
              }
            }
          }
        }
      ],
      "regional": []
    }
  
}

},


"CommonSafetyRequest" : {
    1:{
  "messageId": 21,
  "value": {
    "timeStamp": 123456,
    "msgCnt": 5,
    "id": b'\x12\x34\x56\x78',
    "requests": ["itemA", "itemD", "reserved"],
    "regional": [
      {
        "regionId": 42,
        "regExtValue": b'\x00\x01\x02\x03'  #  directly a bytes object
      }
    ]
  }
},


2: {
    "messageId": 21,
    "value": {
        "requests": ["itemQ"],  # Last enum value from your defined set
        "regional": [
            {
                "regionId": 0,
                "regExtValue": b''  # empty bytes for empty extension
            },
            {
                "regionId": 255,
                "regExtValue": b'\x01'  # fake placeholder for {"x": 1}
            },
            {
                "regionId": 128,
                "regExtValue": bytes.fromhex("deadbeef")  # convert hex string to bytes
            },
            {
                "regionId": 100,
                "regExtValue": b''  # assuming null means no extension data
            }
        ]
    }
}
},

"EVA" : {
    1: {
  "messageId": 21,
  "value": {
    "id": b'\xab\xcd\x12\x34',  # 4-byte TemporaryID
    "rsaMsg": {
      "msgCnt": 1,
      "typeEvent": 7001
    },
    "regional": [
      {
        "regionId": 42,
        "regExtValue": b'\x01\x02'  # assuming raw octet string fallback
      }
    ]
  }
},

    2 : {
  "messageId": 21,
  "value": {
    "rsaMsg": {
      "msgCnt": 2,
      "typeEvent": 8001,
      "description": [8001, 8002],
      "regional": [
        {"regionId": 0, "regExtValue": b'\xde\xad\xbe\xef'},
        {"regionId": 255, "regExtValue": b'\xde\xad\xbe\xef'},
        {"regionId": 42, "regExtValue": b'\xde\xad\xbe\xef'}
      ]
    },
    "responseType": "stationary",
    "details": {
      "sspRights": 2,
      "sirenUse": "inUse",
      "lightsUse": "notInUse",
      "multi": "multiVehicle",
      "events": {
        "sspRights": 3,
        "event": (b'\x2a\x00', 16)  # bits 1, 3, 5 set in 16-bit BIT STRING
      }
    },
    "mass": 180,
    "basicType": "car",
    "vehicleType": "cars-with-trailers",
    "responseEquip": "medical-rescue-unit",
    "responderType": "ambulance-units",
    "regional": [
      {
        "regionId": 1,
       "regExtValue": b'\xde\xad\xbe\xef'
      }
    ]
  }
}
},

"IC" : {
    1 : {
  "messageId": 1,
  "value": {
    "msgCnt": 127,
    "id": b'\x01\x23\x45\x67',  #4-byte octet string
    "timeStamp": 527040,
    "partOne": {
      "msgCnt": 127,
      "id": b'\xff\xff\xff\xff',
      "secMark": 65535,
      "lat": 900000001,
      "long": 1800000001,
      "elev": 61439,
      "accuracy": {
        "semiMajor": 255,
        "semiMinor": 255,
        "orientation": 65535
      },
      "transmission": "unavailable",
      "speed": 8191,
      "heading": 28800,
      "angle": 127,
      "accelSet": {
        "long": 2001,
        "lat": 2001,
        "vert": 127,
        "yaw": 32767
      },
      "brakes": {
        "wheelBrakes": (b'\x11\x11', 5),
        "traction": "engaged",
        "abs": "engaged",
        "scs": "engaged",
        "brakeBoost": "on",
        "auxBrakes": "on"
      },
      "size": {
        "width": 1023,
        "length": 4095
      }
    },
    "path": {
      "initialPosition": {
        "utcTime": {
          "year": 4095,
          "month": 12,
          "day": 31,
          "hour": 31,
          "minute": 60,
          "second": 65535,
          "offset": 840
        },
        "long": 1800000001,
        "lat": 900000001,
        "elevation": 61439,
        "heading": 28800,
        "speed": {
          "transmisson": "unavailable",
          "speed": 8191
        },
        "posAccuracy": {
          "semiMajor": 255,
          "semiMinor": 255,
          "orientation": 65535
        },
        "timeConfidence": "time-000-000-000-000-01",
        "posConfidence": {
          "pos": "a1cm",
          "elevation": "elev-000-01"
        },
        "speedConfidence": {
          "heading": "prec0-0125deg",
          "speed": "prec0-01ms",
          "throttle": "prec0-5percent"
        }
      },
      "currGNSSstatus": (b'\x11\x11', 8),
      "crumbData": [
        {
          "latOffset": 131071,
          "lonOffset": -131072,
          "elevationOffset": 2047,
          "timeOffset": 65535
        }
      ]
    },
    "pathPrediction": {
      "radiusOfCurve": 32767,
      "confidence": 200
    },
    "intersectionID": {
      "region": 65535,
      "id": 65535
    },
    "laneNumber": ("approach", 15),
    
    "eventFlag": (b'\x11\x11', 13),
    "regional": [
      {
        "regionId": 255,
        "regExtValue": b'\xde\xad\xbe\xef'
      }
    ]
  }
},


2 : {
  "messageId": 1,
  "value": {
    "msgCnt": 0,
    "id": b'\x01\x22\x44\x67',
    "intersectionID": {
      "id": 0
    },
    "laneNumber": ("lane", 1),
    "eventFlag": (b'\x12\x10', 13)
  }
}
},

"MAP" :{
    1 : {
    "messageId": 18,
    "value": {
        "timeStamp": 45678,
        "msgIssueRevision": 3,
        "layerType": "intersectionData",
        "layerID": 10,
        "intersections": [
            {
                "name": "MainStreetAnd1stAve",
                "id": {
                    "region": 123,
                    "id": 456
                },
                "revision": 3,
                "refPoint": {
                    "lat": 390000000,
                    "long": -770000000,
                    "elevation": 150,
                    "regional": [
                        {
                            "regionId": 10,
                            "regExtValue": b"\x00\x64\x02"  # Placeholder
                        }
                    ]
                },
                "laneWidth": 300,
                "laneSet": [
                    {
                        "laneID": 1,
                        "laneAttributes": {
                            "directionalUse": (b'\x80', 2),  # Bit 0 set, size : 2 bits
                            "sharedWith": (b'\x20', 1),
                            "laneType": ("vehicle", (b'\xA0', 8))
                        },
                        "nodeList": (
                            "nodes",
                            [
                                {
                                    "delta": (
                                        "node-XY3",
                                        {"x": 10, "y": 20}
                                    )
                                },
                                {
                                    "delta": (
                                        "node-XY3",
                                        {"x": -10, "y": -5}
                                    )
                                }
                            ]
                        )
                    }
                ]
            }
        ],
        "regional": [
            {
                "regionId": 10,
                "regExtValue": b"\x00\x64\x02"  # Placeholder
            }
        ]
    }
},

2: {
    "messageId": 18,
    "value": {
        "timeStamp": 0,  # edge case: lowest valid time
        "msgIssueRevision": 127,  # edge case: max value for MsgCount
        "layerType": "generalMapData",
        "layerID": 100,  # edge case: max allowed LayerID
        "intersections": [
            {
                "name": "EdgeCaseIntersection",
                "id": {
                    "region": 0,  # edge case: min region
                    "id": 0       # edge case: min intersection id
                },
                "revision": 0,
                "refPoint": {
                    "lat": -900000000,   # edge case: min latitude
                    "long": 1800000001,  # edge case: max longitude
                    "elevation": -4096,  # edge case: min elevation
                    "regional": [
                        {
                            "regionId": 1,
                            "regExtValue": b"\xFF\xFF\xFF"  # example encoded extension
                        }
                    ]
                },
                "laneWidth": 0,  # edge case: min width
                "laneSet": [
                    {
                        "laneID": 255,  # edge case: max LaneID
                        "laneAttributes": {
                            "directionalUse": (b'\xC0', 2),  # bits 0 and 1 set (ingress + egress)
                            "sharedWith": (b'\x00', 1),      # no shared flags
                            "laneType": ("crosswalk", (b'\x01\x00', 16))  # sample 16-bit bitstring
                        },
                        "nodeList": (
                            "nodes",
                            [
                                {
                                    "delta": (
                                        "node-XY5",
                                        {"x": 8191, "y": -8192}  # edge Offset-B14
                                    )
                                },
                                {
                                    "delta": (
                                        "node-XY5",
                                        {"x": 0, "y": 0}
                                    )
                                }
                            ]
                        )
                    }
                ]
            }
        ],
        "regional": [
            {
                "regionId": 255,  # edge case: max region ID
                "regExtValue": b"\xAB\xCD"  # placeholder
            }
        ]
    }
}
},

"NMEA" :{
    1 : {
    "messageId": 28,  # Arbitrary valid message ID (0–127)
    "value": {
        "timeStamp": 123456,          # MinuteOfTheYear (within 0–527040)
        "rev": "rev2",                # One of the ENUM values
        "msg": 1001,                  # Any value from 0–32767
        "wdCount": 3,                 # ObjectCount: how many data blocks in payload
        "payload": b"$GPGGA,123519.00,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47",  # NMEA-encoded sentence
        "regional": [
            {
                "regionId": 10,
                "regExtValue": b"\x01\x02"  # Placeholder raw extension data
            }
        ]
    }
},

2 : {
    "messageId": 23,  # Edge case: minimum valid message ID
    "value": {
        "payload": b"$GPRMC,000000,A,0000.0000,N,00000.0000,E,0.00,0.00,010180,,,A*68"  # Minimal sentence
        # All optional fields are omitted
    }
}
},

"PSM" : { 
    1:{
    "messageId": 20,
    "value": {
        "basicType": "aPEDESTRIAN",
        "secMark": 65535,
        "msgCnt": 127,
        "id": b'\x12\x34\x56\x78',
        "position": {
            "lat": 900000001,
            "long": 1800000001,
            "elevation": 61439,
            "regional": [
                {
                    "regionId": 1,
                    "regExtValue": b'\x00\x0C\x34'
                }
            ]
        },
        "accuracy": {
            "semiMajor": 255,
            "semiMinor": 255,
            "orientation": 65535
        },
        "speed": 8191,
        "heading": 28800,
        "accelSet": {
            "long": 2001,
            "lat": -2000,
            "vert": 127,
            "yaw": 32767
        },
        "pathHistory": {
            "initialPosition": {
                "utcTime": {
                    "year": 4095,
                    "month": 12,
                    "day": 31,
                    "hour": 31,
                    "minute": 60,
                    "second": 65535,
                    "offset": 840
                },
                "long": 1800000001,
                "lat": 900000001,
                "elevation": 61439,
                "heading": 28800,
                "speed": {
                    "transmisson": "unavailable",
                    "speed": 8191
                },
                "posAccuracy": {
                    "semiMajor": 255,
                    "semiMinor": 255,
                    "orientation": 65535
                },
                "timeConfidence": "time-000-000-000-000-01",
                "posConfidence": {
                    "pos": "a1cm",
                    "elevation": "elev-000-01"
                },
                "speedConfidence": {
                    "heading": "prec0-0125deg",
                    "speed": "prec0-01ms",
                    "throttle": "prec0-5percent"
                }
            },
            "currGNSSstatus": (b'\xAA', 8),
            "crumbData": [
                {
                    "latOffset": 131071,
                    "lonOffset": -131072,
                    "elevationOffset": 2047,
                    "timeOffset": 65535,
                    "speed": 8191,
                    "posAccuracy": {
                        "semiMajor": 255,
                        "semiMinor": 255,
                        "orientation": 65535
                    },
                    "heading": 240
                }
            ]
        },
        "pathPrediction": {
            "radiusOfCurve": 32767,
            "confidence": 200
        },
        "propulsion": ("motor", "bicycle"),
        "crossRequest": True,
        "crossState": False,
        "clusterSize": "medium",
        "clusterRadius": 100,
        "eventResponderType": "lawEnforcement",
        "attachment": "bicycleTrailer",
        "attachmentRadius": 200,
        "animalType": "serviceUse",
        "regional": [
            {
                "regionId": 5,
                "regExtValue": b'\x01\x02\x03'  # region-specific encoded extension
            }
        ]
    }
},

2 : {
    "messageId": 20,
    "value": {
        "basicType": "aPEDALCYCLIST",
        "secMark": 12345,
        "msgCnt": 5,
        "id": b'\xAB\xCD\xEF\x01',
        "position": {
            "lat": 420000000,
            "long": -750000000,
            "elevation": 250,
            "regional": [
                {
                    "regionId": 2,
                    "regExtValue": b'\x12\x34\x56'  # dummy encoded region data
                }
            ]
        },
        "accuracy": {
            "semiMajor": 100,
            "semiMinor": 80,
            "orientation": 4500
        },
        "speed": 1500,
        "heading": 12000,
        "accelSet": {
            "long": 100,
            "lat": -50,
            "vert": 5,
            "yaw": 120
        },
        "pathHistory": {
            "initialPosition": {
                "utcTime": {
                    "year": 2025,
                    "month": 6,
                    "day": 17,
                    "hour": 14,
                    "minute": 30,
                    "second": 30000,
                    "offset": 0
                },
                "long": -750000000,
                "lat": 420000000,
                "elevation": 250,
                "heading": 12000,
                "speed": {
                    "transmisson": "forwardGears",
                    "speed": 1500
                },
                "posAccuracy": {
                    "semiMajor": 100,
                    "semiMinor": 80,
                    "orientation": 4500
                },
                "timeConfidence": "time-000-010",
                "posConfidence": {
                    "pos": "a50cm",
                    "elevation": "elev-050-00"
                },
                "speedConfidence": {
                    "heading": "prec05deg",
                    "speed": "prec5ms",
                    "throttle": "prec1percent"
                }
            },
            "currGNSSstatus": (b'\x55', 8),
            "crumbData": [
                {
                    "latOffset": 1000,
                    "lonOffset": -1000,
                    "elevationOffset": 5,
                    "timeOffset": 100,
                    "speed": 1200,
                    "posAccuracy": {
                        "semiMajor": 50,
                        "semiMinor": 50,
                        "orientation": 2000
                    },
                    "heading": 180
                }
            ]
        },
        "pathPrediction": {
            "radiusOfCurve": 1000,
            "confidence": 95
        },
        "propulsion": ("human", "onFoot"),
        "crossRequest": False,
        "crossState": True,
        "clusterSize": "small",
        "clusterRadius": 20,
        "eventResponderType": "aDOTWorker",
        "attachment": "stroller",
        "attachmentRadius": 50,
        "animalType": "pet",
        "regional": [
            {
                "regionId": 3,
                "regExtValue": b'\xAA\xBB\xCC'
            }
        ]
    }
}
},


"PDM" : {
    1:{
    "messageId": 25,
    "value": {
        "timeStamp": 123456,
        "sample": {
            "sampleStart": 10,
            "sampleEnd": 30
        },
        "directions": (b'\x0F\xF0', 16),  # all directions on (16 bits set)
        "term": ("termtime", 600),
        "snapshot": (
            "snapshotTime",
            {
                "speed1": 15,
                "time1": 10,
                "speed2": 20,
                "time2": 30
            }
        ),
        "txInterval": 5,
        "dataElements": [
            {
                "dataType": "speedC",
                "subType": 3,
                "sendOnLessThenValue": -100,
                "sendOnMoreThenValue": 100,
                "sendAll": True
            },
            {
                "dataType": "yaw",
                "sendAll": False
            }
        ],
        "regional": [
            {
                "regionId": 1,
                "regExtValue": b'\xAA\xBB\xCC'
            }
        ]
    }
},

2 : {
    "messageId": 25,
    "value": {
        "sample": {
            "sampleStart": 5,
            "sampleEnd": 15
        },
        "directions": (b'\x01\x00', 16),  # only direction 0 on
        "term": ("termDistance", 1000),
        "snapshot": (
            "snapshotDistance",
            {
                "distance1": 50,
                "speed1": 10,
                "distance2": 100,
                "speed2": 20
            }
        ),
        "txInterval": 10,
        "dataElements": [
            {
                "dataType": "airTemp",
                "subType": 2,
                "sendAll": True
            }
        ]
        # no regional or timeStamp included
    }
}
},

"PVD" :{
    1:{
  "messageId": 37,
  "value": {
    "startVector": {
      "long": 100000000,
      "lat": 200000000
    },
    "vehicleType": {
      "keyType": 1,
      "role": "basicVehicle",
      "iso3883": 23,
      "hpmsType": "car",
      "vehicleType": "cars",
      "responseEquip": "aircraft",
      "responderType": "emergency-vehicle-units",
      "fuelType": 3
    },
    "snapshots": [
      {
        "thePosition": {
          "long": 100000100,
          "lat": 200000200
        }
      }
    ]
  }
},

2 :{
  "messageId": 37,
  "value": {
    "timeStamp": 100000,
    "segNum": 15,
    "probeID": {
      "vin": b"1HGCM82633A004352"
    },
    "startVector": {
      "long": 110000000,
      "lat": 210000000,
      "elevation": 300,
      "heading": 9000,
      "speed": {
        "transmisson": "forwardGears",
        "speed": 1500
      }
    },
    "vehicleType": {
      "keyType": 2,
      "role": "emergency",
      "iso3883": 45,
      "hpmsType": "bus",
      "vehicleType": "heavy-vehicles",
      "responseEquip": "marine-equipment",
      "responderType": "state-police-units",
      "fuelType": 2
    },
    "snapshots": [
      {
        "thePosition": {
          "long": 110000100,
          "lat": 210000100
        },
        "safetyExt": {
          
        },
        "dataSet": {
          "airTemp": 55,
          "steering": {
            "angle": -10
          },
          "throttlePos": 85
        }
      }
    ]
  }
}
},

"RSA" :{
    1: {
    "messageId": 36,
    "value": {
        "msgCnt": 1,
        "typeEvent": 512,
        "timeStamp": 45678,
        "heading": (b'\x10\x00', 16),  # BIT STRING: only one bit (bit 4) set
        "extent": "useFor100meters",
        "position": {
            "long": 120000000,
            "lat": 800000000,
            "elevation": 150,
            "heading": 14400,
            "speed": {
                "transmisson": "neutral",
                "speed": 300
            }
        }
    }
},


2 : {
    "messageId": 36,
    "value": {
        "msgCnt": 2,
        "timeStamp": 123456,
        "typeEvent": 1024,
        "description": [1025, 1026],
        "priority": b'\x01',
        "heading": (b'\x05\x00', 16),  # BIT STRING, 2 bytes, 16 bits set as example
        "extent": "useFor100meters",
        "position": {
            "utcTime": {
                "year": 2023,
                "month": 6,
                "day": 17,
                "hour": 14,
                "minute": 30,
                "second": 12345,
                "offset": 300
            },
            "long": 123456789,
            "lat": 987654321,
            "elevation": 500,
            "heading": 10000,
            "speed": {
                "transmisson": "forwardGears",
                "speed": 1024
            },
            "posAccuracy": {
                "semiMajor": 50,
                "semiMinor": 40,
                "orientation": 1000
            },
            "timeConfidence": "time-000-100",
            "posConfidence": {
                "pos": "a20cm",
                "elevation": "elev-000-10"
            },
            "speedConfidence": {
                "heading": "prec0-1deg",
                "speed": "prec0-1ms",
                "throttle": "prec0-5percent"
            }
        },
        "furtherInfoID": b'\xAB\xCD',
        "regional": [
            {
                "regionId": 1,
                "regExtValue": b'\x01\x02\x03\x04'  # Region-specific binary data
            }
        ]
    }
}
},

"RTCM" : {
    1:{
    "messageId": 38,
    "value": {
        "msgCnt": 5,
        "rev": "rtcmRev3",
        "msgs": [
            b"\x01\x02\x03\x04",
            b"\x0A\x0B\x0C"
        ]
    }
},


2: {
    "messageId": 38,
    "value": {
        "msgCnt": 10,
        "rev": "rtcmRev3",
        "timeStamp": 345600,
        "anchorPoint": {
            "long": 123456789,
            "lat": 987654321,
            "elevation": 450,
            "heading": 14400,
            "speed": {
                "transmisson": "forwardGears",
                "speed": 650
            },
            "posAccuracy": {
                "semiMajor": 40,
                "semiMinor": 35,
                "orientation": 12000
            },
            "timeConfidence": "time-000-100",
            "posConfidence": {
                "pos": "a5m",
                "elevation": "elev-050-00"
            },
            "speedConfidence": {
                "heading": "prec01deg",
                "speed": "prec5ms",
                "throttle": "prec10percent"
            }
        },
        "rtcmHeader": {
            "status": (b"\xA3", 8),
            "offsetSet": {
                "antOffsetX": 100,
                "antOffsetY": -128,
                "antOffsetZ": 250
            }
        },
        "msgs": [
            b"\x12\x34\x56",
            b"\xAB\xCD",
            b"\x00\x11\x22"
        ]
    }
}
},

"SRM" : {
    1:{
    "messageId": 20,
    "value": {
        "second": 45000,
        "requestor": {
            "id": ("stationID", 123456789)
        }
    }
},

2 : {
  "messageId": 27,
  "value": {
    "timeStamp": 345600,
    "second": 45000,
    "sequenceNumber": 78,
    "requests": [
      {
        "request": {
          "id": {
            "region": 1234,
            "id": 5678
          },
          "requestID": 12,
          "requestType": "priorityRequestUpdate",
          "inBoundLane": ("lane", 4),
          "outBoundLane": ("approach", 2)
        },
        "minute": 345600,
        "second": 45000,
        "duration": 300
      }
    ],
    "requestor": {
      "id": ("stationID", 987654321),
      "type": {
        "role": "transit",
        "subrole": "requestSubRole5",
        "request": "requestImportanceLevel7",
        "hpmsType": "car"
      },
      "position": {
        "position": {
          "lat": 400000000,
          "long": -730000000,
          "elevation": 1200
        },
        "heading": 12000,
        "speed": {
          "transmisson": "forwardGears",
          "speed": 1600
        }
      },
      "name": "MetroX",
      "routeName": "LineBlue",
      "transitStatus": (b'\x21', 8),  # loading and charging
      "transitOccupancy": "occupancyVeryLow",
      "transitSchedule": -5
    }
  }
}
},

"SSM" :{
    1:{
  "messageId": 28,
  "value": {
    "timeStamp": 123000,
    "second": 15000,
    "sequenceNumber": 10,
    "status": [
      {
        "sequenceNumber": 10,
        "id": {
          "region": 5,
          "id": 3001
        },
        "sigStatus": [
          {
            "requester": {
              "id": ("stationID", 321654987),
              "request": 7,
              "sequenceNumber": 10,
              "role": "publicTransport",
              "typeData": {
                "role": "publicTransport",
                "subrole": "requestSubRole2",
                "request": "requestImportanceLevel5",
                "iso3883": 33,
                "hpmsType": "bus"
              }
            },
            "inboundOn": ("approach", 3),
            "outboundOn": ("lane", 5),
            "minute": 123000,
            "second": 15000,
            "duration": 60,
            "status": "watchOtherTraffic"
          }
        ]
      }
    ]
  }
},

2 : {
  "messageId": 28,
  "value": {
    "timeStamp": 451234,
    "second": 54321,
    "sequenceNumber": 99,
    "status": [
      {
        "sequenceNumber": 2,
        "id": {
          "region": 10,
          "id": 5002
        },
        "sigStatus": [
          {
            "requester": {
              "id": ("stationID", 3654987),
              "request": 42,
              "sequenceNumber": 2,
              "role": "emergency",
              "typeData": {
                "role": "emergency",
                "subrole": "requestSubRole4",
                "request": "requestImportanceLevel3",
                "iso3883": 14,
                "hpmsType": "car"
              }
            },
            "inboundOn": ("lane", 6),
            "outboundOn": ("approach", 1),
            "minute": 451234,
            "second": 54321,
            "duration": 100,
            "status": "processing"
          }
        ]
      }
    ]
  }
}
},

"SPAT" :{
    1: {
    "messageId": 13,
    "value": {
        "timeStamp": 123456,
        "name": "SPAT_MainStreet",
        "intersections": [
            {
                "name": "Main_St_Intersection",
                "id": {
                    "region": 100,
                    "id": 12
                },
                "revision": 5,
                "status": (b'\x20\x00', 14),  # IntersectionStatusObject: 14 bits, example bitmap
                "moy": 123456,
                "timeStamp": 45678,
                "enabledLanes": [1, 2, 3],
                "states": [
                    {
                        "movementName": "StraightThrough",
                        "signalGroup": 1,
                        "state-time-speed": [
                            {
                                "eventState": "protected-Movement-Allowed",
                                "timing": {
                                    "startTime": 100,
                                    "minEndTime": 1200,
                                    "maxEndTime": 1500,
                                    "likelyTime": 1300,
                                    "confidence": 2,  # TimeIntervalConfidence ENUM: 2 : prec10ms
                                    "nextTime": 1600
                                },
                                "speeds": [
                                    {
                                        "type": "ecoDrive",
                                        "speed": 45,
                                        "confidence": "prec10ms",  # ENUM as string is OK for asn1tools
                                        "distance": 150,
                                        "class": 1
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
}
},

"TM00" :{
    1 : { 
  "messageId": 127,
  "value": {
    "header": {
      "hostStaticId": "HOST123456789012",
      "targetStaticId": "TARGET1234567890",
      "hostBSMId": "ABC12345",
      "planId": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2024-06-24T15:30:45"
    },
    "body": {
      "strategy": "PlatoonMergeStrategy",
      "planType": "platoonFollowerJoin",
      "urgency": 1000,
      "location": {
        "ecefX": 638363700,
        "ecefY": -638363700,
        "ecefZ": 0,
        "timestamp": "2024-06-24T15:30:46"
      },
      "strategyParams": "lane:2,speed:13.5,acceleration:1.2,preferred_gap:5.5,mergeTime:8.1",
      "trajectoryStart": {
        "ecefX": -638363700,
        "ecefY": 0,
        "ecefZ": 638363700,
        "timestamp": "2024-06-24T15:30:47"
      },
      "trajectory": [
        { "offsetX": -500, "offsetY": 0, "offsetZ": 500 },
        { "offsetX": 1, "offsetY": -1, "offsetZ": 1 }
      ],
      "expiration": "2024-06-24T15:31:00"
    }
  }
},

2 : {
  "messageId": 0,
  "value": {
    "header": {
      "hostStaticId": "H1",
      "targetStaticId": "T1",
      "hostBSMId": "ABCDEFGH",
      "planId": "00000000-0000-0000-0000-000000000000",
      "timestamp": "2024-01-01T00:00:00"
    },
    "body": {
      "strategy": "S1",
      "planType": "unknown",
      "urgency": 0,
      "location": {
        "ecefX": 0,
        "ecefY": 0,
        "ecefZ": 0,
        "timestamp": "2024-01-01T00:00:01"
      },
      "strategyParams": "a!"
    }
  }
}
},

"TM01" :{
    1: {
  "messageId": 8,
  "value": {
    "header": {
      "hostStaticId": "HOST_UNIT_001234",
      "targetStaticId": "TARGET_UNIT_998877",
      "hostBSMId": "BSMID001",
      "planId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "timestamp": "2024-06-24T18:45:30"
    },
    "body": {
      "urgency": 1000,
      "isAccepted": True
    }
  }
},

2 : {
  "messageId": 8,
  "value": {
    "header": {
      "hostStaticId": "H1",
      "targetStaticId": "T2",
      "hostBSMId": "ABCDEFGH",
      "planId": "00000000-0000-0000-0000-000000000000",
      "timestamp": "2024-01-01T00:00:00"
    },
    "body": {
      "urgency": 0,
      "isAccepted": False
    }
  }
}
},

"TM02" :{
    1:{
  "messageId": 2,
  "value": {
    "header": {
      "hostStaticId": "HOST_ECU_123456",
      "targetStaticId": "TARGET_UNIT_999",
      "hostBSMId": "BSM12345",
      "planId": "123e4567-e89b-12d3-a456-426614174000",
      "timestamp": "2025-06-24T17:30:00"
    },
    "body": {
      "location": {
        "ecefX": 638363700,
        "ecefY": -638363700,
        "ecefZ": 0,
        "timestamp": "2025-06-24T17:30:01"
      },
      "trajectory": [
        { "offsetX": 500, "offsetY": -500, "offsetZ": 0 },
        { "offsetX": -100, "offsetY": 250, "offsetZ": 20 },
        { "offsetX": 0, "offsetY": 0, "offsetZ": -50 }
      ]
    }
  }
},

2 : {
  "messageId": 2,
  "value": {
    "header": {
      "hostStaticId": "H1",
      "targetStaticId": "T2",
      "hostBSMId": "ABCDEFGH",
      "planId": "00000000-0000-0000-0000-000000000000",
      "timestamp": "2023-01-01T00:00:00"
    },
    "body": {
      "location": {
        "ecefX": -638363700,
        "ecefY": 638363700,
        "ecefZ": -1,
        "timestamp": "2023-01-01T00:00:01"
      },
      "trajectory": []
    }
  }
}
},

"TM03" : {
    1: {
    "messageId": 3,
    "value": {
        "header": {
            "hostStaticId": "HOST_STATIC_ID_16",
            "targetStaticId": "TARGET_STATIC_15",
            "hostBSMId": "ABCDEFGH",
            "planId": "123e4567-e89b-12d3-a456-426614174000",
            "timestamp": "2025-06-24T17:45:00"
        },
        "body": {
            "strategy": "KeepRightAndAccelerateToMergeZoneQuickly",
            "operationParams": "max-speed:27.5;gap:1.5;acceleration:3.2;confidence:high;mergePoint:5;lane:2"
        }
    }
},

2 : {
    "messageId": 3,
    "value": {
        "header": {
            "hostStaticId": "H1",
            "targetStaticId": "T1",
            "hostBSMId": "B1234567",
            "planId": "00000000-0000-0000-0000-000000000000",
            "timestamp": "2023-01-01T00:00:00"
        },
        "body": {
            "strategy": "Go",
            "operationParams": "ok"
        }
    }
}
},

"TM04" : {
    1 : {
    "messageId": 4,
    "value": {
        "header": {
            "year": 4095,
            "timeStamp": 527040,
            "secMark": 65535,
            "msgIssueRevision": 127
        },
        "regional": 
            {
                "regionId": 1,
                "regExtValue": b"\xDE\xAD\xBE\xEF"  # placeholder for custom extension bytes
            }
        
    }
},

2 : {
    "messageId": 4,
    "value": {
        # both 'header' and 'regional' omitted as OPTIONAL
    }
}
},

"TM05" :{
    1: {
    "messageId": 25,
    "value": {
        "header": {
            "year": 2023,
            "timeStamp": 263520,     # Mid-year (~June)
            "secMark": 32768,        # Half of DSecond range
            "msgIssueRevision": 64   # Mid-point of MsgCount
        },
        "regional": {
            "regionId": 10,          # Hypothetical valid region ID
            "regExtValue": b"\x01\x23\x45\x67"  # Example payload
        }
    }
},

2 : {
    "messageId": 127,  # Max of DSRCmsgID
    "value": {
        # Omitting header to test optional field handling
        "regional": {
            "regionId": 255,         # Max valid region ID
            "regExtValue": b"\xFF\xFF\xFF\xFF"  # All-byte edge case
        }
    }
}
},

"TM06" : {
    1:{
    "messageId": 42,
    "value": {
        "header": {
            "year": 2024,
            "timeStamp": 123456,     # A valid minute of the year
            "secMark": 50000,        # A valid second within the year
            "msgIssueRevision": 33   # A valid MsgCount
        },
        "regional": {
            "regionId": 22,                      # Arbitrary regionId
            "regExtValue": b"\xCA\xFE\xBA\xBE"   # Random byte pattern for testing
        }
    }
},

2 : {
    "messageId": 0,  # Lowest valid DSRCmsgID
    "value": {
        # Header is optional and omitted here
        "regional": {
            "regionId": 255,                   # Max region ID
            "regExtValue": b"\x00" * 8         # Minimal test payload (8 null bytes)
        }
    }
}
},

"TM07" :{
    1: {
    "messageId": 7,
    "value": {
        "header": {
            "year": 2025,
            "timeStamp": 345600,     # Represents ~240th day of the year
            "secMark": 45000,        # ~12.5 hours into the day
            "msgIssueRevision": 100
        },
        "regional": {
            "regionId": 44,
            "regExtValue": b"\xAB\xCD\xEF"  # Random example payload
        }
    }
},
2 : {
    "messageId": 0,  # Minimum valid value for DSRCmsgID
    "value": {
        "regional": {
            "regionId": 0,                   # Minimum regionId
            "regExtValue": b""               # Empty payload (still valid if handled gracefully)
        }
    }
}
},

"TM08" :{
    1: {
    "messageId": 8,
    "value": {
        "header": {
            "year": 2024,
            "timeStamp": 123456,           # Mid-year value
            "secMark": 32000,              # ~9 hours into the day
            "msgIssueRevision": 42
        },
        "regional": {
            "regionId": 128,
            "regExtValue": b"\xDE\xAD\xBE\xEF"  # Example region-specific payload
        }
    }
},

2 : {
    "messageId": 0,  # Edge: lowest valid DSRCmsgID
    "value": {
        "regional": {
            "regionId": 0,           # Edge: minimum valid RegionId
            "regExtValue": b""       # Edge: empty but valid extension
        }
    }
}
},

"TM09" :{
    1: {
    "messageId": 9,
    "value": {
        "header": {
            "year": 2025,
            "timeStamp": 520000,          # Edge: near upper bound of MinuteOfTheYear
            "secMark": 65535,             # Max DSecond
            "msgIssueRevision": 127       # Max MsgCount
        },
        "regional": {
            "regionId": 255,              # Max RegionId
            "regExtValue": b'\xFE\xED\xFA\xCE'  # Sample payload
        }
    }
},

2 : {
    "messageId": 1,  # Low-end DSRCmsgID
    "value": {
        "regional": {
            "regionId": 0,                # Min RegionId
            "regExtValue": b''            # Edge: empty extension data
        }
    }
}
},

"TM10" :{
    1: {
    "messageId": 10,
    "value": {
        "header": {
            "year": 4095,                  # Max DYear
            "timeStamp": 527040,           # Max MinuteOfTheYear
            "secMark": 65535,              # Max DSecond
            "msgIssueRevision": 127        # Max MsgCount
        },
        "regional": {
            "regionId": 255,               # Max RegionId
            "regExtValue": b'\xCA\xFE\xBA\xBE'  # Sample payload
        }
    }
},

2 : {
    "messageId": 0,  # Min DSRCmsgID
    "value": {
        "regional": {
            "regionId": 0,                 # Min RegionId
            "regExtValue": b''             # Edge: empty extension
        }
    }
}
}
}



# Compile ASN.1 schema with PER encoding
spec = asn1tools.compile_files('messages/TestMessage10.asn1', 'per')

# Encode into UPER (Unaligned Packed Encoding Rules)
encoded = spec.encode('MessageFrame', messages['TM10'][1])

# Print hex string
print(encoded)
